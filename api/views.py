#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.
import hashlib
import logging
import os
import tempfile
import time
from io import BytesIO

import cv2
from PIL import Image
from PIL.JpegImagePlugin import JpegImageFile
from django.core.exceptions import ValidationError
from django.core.files.base import ContentFile
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.db.models import Max
from django.http import JsonResponse, HttpResponse, Http404
from django.views.decorators.csrf import csrf_exempt
from filetype import filetype
from filetype.types import IMAGE, VIDEO
from rest_framework.decorators import api_view
from rest_framework.exceptions import MethodNotAllowed
from rest_framework.generics import get_object_or_404

from api.models import Post, File, Thread, Board
from api.serializers import PostSerializer, ThreadSerializer, BoardSerializer

log = logging.getLogger(__name__)


@api_view(["GET"], )
@csrf_exempt
def get_all_boards(request):
    boards = Board.objects.all()
    serializer = BoardSerializer(boards, many=True)
    return JsonResponse(serializer.data, safe=False)


@api_view(["GET"], )
@csrf_exempt
def get_all_threads(request, board_name, page):
    per_page = 10
    threads = Thread.objects \
                  .filter(board__board_name=board_name) \
                  .annotate(Max('posts__created_at')) \
                  .order_by('-posts__created_at__max')[page * per_page: (page + 1) * per_page]
    board = get_object_or_404(Board, board_name=board_name)
    threads_list = []
    for thread in threads:
        thread_posts = thread.posts.prefetch_related('files')
        obj = {
            'pinned': thread.pinned,
            'closed': thread.closed,
            'posts': [],
        }
        obj['posts'].append(PostSerializer(thread_posts.first()).data)  # OP-post
        latest_posts_reversed = PostSerializer(thread_posts.reverse().all()[:3], many=True).data  # 3 latest posts
        if thread_posts.count() < 4:
            latest_posts_reversed = latest_posts_reversed[:-1]  # cut last post (OP-post)
        obj['posts'].extend(reversed(latest_posts_reversed))
        threads_list.append(obj)

    result = {
        'board': BoardSerializer(board).data,
        'threads': threads_list,
    }
    return JsonResponse(result)


@api_view(["GET"], )
@csrf_exempt
def get_thread(request, board_name, thread_id):
    try:
        thread_qs = Thread.objects
        thread_qs = ThreadSerializer.setup_eager_loading(thread_qs)
        serializer = ThreadSerializer(thread_qs.get(board__board_name=board_name, posts__id=thread_id))
    except (TypeError, ValueError, ValidationError, Thread.DoesNotExist):
        log.info('No such thread.', exc_info=True)
        raise Http404()
    return JsonResponse(serializer.data, safe=False)


@api_view(["POST"], )
@csrf_exempt
def create_thread(request, board_name):
    pass


@api_view(["GET"], )
@csrf_exempt
def get_post(request, board_name, thread_id, post_id):
    post = get_object_or_404(Post, post_id=post_id, thread__board__board_name=board_name)
    serializer = PostSerializer(post)
    return JsonResponse(serializer.data, safe=False)


@api_view(["POST"], )
@csrf_exempt
def create_post(request, board_name, thread_id):
    pass


@api_view(["GET"], )
@csrf_exempt
def get_file(request, file_hash):
    file = get_object_or_404(File, hash=file_hash)
    with file.content.open('rb') as fd:
        return HttpResponse(fd.read(), content_type='application/octet-stream')


@api_view(["GET"], )
@csrf_exempt
def get_thumbnail(request, file_hash):
    file = get_object_or_404(File, hash=file_hash)
    with file.preview_content.open('rb') as fd:
        return HttpResponse(fd.read(), content_type='application/octet-stream')


@csrf_exempt
def upload_file(request, board_name):
    if request.method != 'POST':
        return MethodNotAllowed(request.method)

    result = []

    max_file_size = get_object_or_404(Board, board_name=board_name).max_file_size * 1024
    file: InMemoryUploadedFile
    for filename, file in request.FILES.items():
        data = file.read(max_file_size + 1)
        if len(data) > max_file_size:
            file.close()
            result.append({
                filename: {
                    'success': False,
                    'details': f'Файл слишком большой, максимальный размер: {max_file_size / 1024}KB'
                }
            })
            continue
        ext_start = time.time()
        fformat = filetype.guess(data)
        log.info('Time to detect fformat: %s', ext_start - time.time())
        try:
            log.info('Detected mime: %s, fmt: %s', fformat.MIME, fformat.EXTENSION)
        except:
            pass
        if fformat is None or not File.FileTypeEnum.has_value(fformat.EXTENSION):
            result.append({
                filename: {
                    'success': False,
                    'details': f'Файл неверного типа ({fformat.MIME if fformat is not None else "неизвестно"}),'
                    f' разрешены: {list(File.FileTypeEnum.list_values())} '
                }
            })
            continue

        file_hash = hashlib.sha512(data).hexdigest()
        if File.objects.filter(hash=file_hash).exists():
            result.append({
                filename: {
                    'success': True,
                    'hash': file_hash
                }
            })
            continue

        if fformat in IMAGE:
            max_thumb_size = 250
            image = Image.open(BytesIO(data))
            resize_ratio = min(max_thumb_size / image.width, max_thumb_size / image.height)
            thumbnail = image.resize((int(image.width * resize_ratio), int(image.height * resize_ratio)),
                                     Image.LANCZOS)
            thumbnail = thumbnail.convert('RGB')
            thumbnail_bytes = BytesIO()
            thumbnail.save(thumbnail_bytes, format='JPEG', quality=70)

            model_file = File(
                hash=file_hash,
                filename=filename,
                width=image.width,
                height=image.height,
                size=len(data),
                thumbnailWidth=thumbnail.width,
                thumbnailHeight=thumbnail.height,
                filetype=fformat.EXTENSION
            )
            model_file.content.save(f'c_{file_hash}', ContentFile(data))
            model_file.preview_content.save(f'p_{file_hash}', ContentFile(thumbnail_bytes.getvalue()))
            model_file.save()

            result.append({
                filename: {
                    'success': True,
                    'hash': file_hash
                }
            })
        elif fformat in VIDEO:
            temp_file = os.path.join(tempfile.gettempdir(), f'{file_hash}.webm')
            with open(temp_file, 'wb') as fd:
                fd.write(data)
            vid = cv2.VideoCapture(temp_file)
            _, frame = vid.read()
            vid.release()
            os.remove(temp_file)
            temp_file = os.path.join(tempfile.gettempdir(), f'{file_hash}.jpg')
            cv2.imwrite(temp_file, frame)

            with open(temp_file, 'rb') as fd:
                max_thumb_size = 250
                thumbnail: JpegImageFile = Image.open(fd)
                width = thumbnail.width
                height = thumbnail.height
                resize_ratio = min(max_thumb_size / width, max_thumb_size / height)
                thumbnail = thumbnail.resize((int(width * resize_ratio), int(height * resize_ratio)),
                                             Image.LANCZOS)
                thumbnail = thumbnail.convert('RGB')
                thumbnail_bytes = BytesIO()
                thumbnail.save(thumbnail_bytes, format='JPEG', quality=85)
            os.remove(temp_file)
            model_file = File(
                hash=file_hash,
                filename=filename,
                width=width,
                height=height,
                size=len(data),
                thumbnailWidth=thumbnail.width,
                thumbnailHeight=thumbnail.height,
                filetype=fformat.EXTENSION
            )
            model_file.content.save(f'c_{file_hash}', ContentFile(data))
            model_file.preview_content.save(f'p_{file_hash}', ContentFile(thumbnail_bytes.getvalue()))
            model_file.save()

            result.append({
                filename: {
                    'success': True,
                    'hash': file_hash
                }
            })

    return JsonResponse({'response': result})
