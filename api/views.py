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
"""
Реализация методов API.
"""

import hashlib
import logging
import os
import tempfile
from io import BytesIO
from typing import Dict, Union

import cv2
from PIL import Image
from PIL.JpegImagePlugin import JpegImageFile
from django.core.exceptions import ValidationError
from django.core.files.base import ContentFile
from django.db import IntegrityError, DataError
from django.http import JsonResponse, Http404
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from filetype import filetype
from filetype.types import IMAGE, VIDEO
from rest_framework.decorators import api_view
from rest_framework.exceptions import MethodNotAllowed
from rest_framework.generics import get_object_or_404
from rest_framework.parsers import JSONParser

from api.models import Post, File, Thread, Board
from api.serializers import PostSerializer, ThreadSerializer, BoardSerializer, FileSerializer

log = logging.getLogger(__name__)

THREADS_PER_PAGE = 10


def create_post_or_thread(request, board_name, thread_id=None) -> JsonResponse:
    """
    Создает пост в указанный тред по ``thread_id``, или, если аргумент не указан,
    создает новый тред.

    :param request: Запрос с JSON.
    :param board_name: Доска, где создавать пост/тред.
    :param thread_id: Номер треда, где создавать пост или ``None``.
    :raise Http404: Если доска или тред не найдены (и указан ``thread_id``).
    """
    try:
        board = get_object_or_404(Board, board_name=board_name)
        if board.closed:
            return JsonResponse({'success': False, 'details': 'Доска закрыта.'})
        if thread_id is not None:  # Если не создаем тред, а постим в существующий
            thread = board.threads.get(posts__id=thread_id)
            if thread.closed:
                return JsonResponse({'success': False, 'details': 'Тред закрыт.'})
    except (TypeError, ValueError, ValidationError, Thread.DoesNotExist):
        log.info('No such thread to post in.')
        raise Http404()
    data: Dict = JSONParser().parse(request)
    try:
        files = File.objects.filter(hash__in=data.pop('files')).all()
    except KeyError:
        return JsonResponse({'success': False, 'details': 'Нельзя создать тред без файла.'})
    if len(files) > 4:
        return JsonResponse({'success': False, 'details': 'Нельзя постить больше четырех файлов.'})
    if thread_id is None and len(files) == 0:
        return JsonResponse({'success': False, 'details': 'Нельзя создать тред без файла.'})
    # TODO: captcha
    # TODO: tripcode processing
    # TODO: text size check
    # TODO: rate limiting
    try:
        if thread_id is None:
            thread = Thread.objects.create(
                pinned=False,
                closed=False,
                board=board,
                last_bump_time=timezone.now()
            )
            thread.save()
        # noinspection PyBroadException
        try:
            new_post_id = Post.objects.filter(thread__board=board).last().post_id + 1
        except Exception:
            log.warning('Unknown new post id...', exc_info=True)
            new_post_id = 1
        email = data.get('email', '')
        # noinspection PyUnboundLocalVariable
        post = Post.objects.create(
            post_id=new_post_id,
            text=data.get('text', None),
            email=email,
            name=data.get('name', None) or board.default_name,
            subject=data.get('subject', ''),
            trip_code=data.get('trip_code', ''),
            op=data.get('op', False),
            thread=thread
        )
        if thread_id is not None and email != "sage" and thread.posts.count() <= board.bump_limit:
            thread.last_bump_time = timezone.now()
    except (IntegrityError, DataError) as e:
        info = e.args[0].split('\n')[0]
        return JsonResponse({'success': False, 'details': f'Не все необходимые поля заполнены: {info}'})
    except ValidationError as e:
        return JsonResponse({'success': False, 'details': ', '.join(e.messages)})
    post.files.add(*files)
    try:
        post.full_clean()
    except ValidationError as e:
        return JsonResponse({'success': False, 'errors': e.message_dict})
    post.save()
    thread.save()
    while board.threads.count() > THREADS_PER_PAGE * board.pages:
        thread_to_delete = board.threads.last()
        log.debug('Deleting %s...', thread_to_delete)
        thread_to_delete.delete()
    return JsonResponse({'success': True, 'data': PostSerializer(post).data}, safe=False)


@api_view(["GET"], )
@csrf_exempt
def get_all_boards(request) -> JsonResponse:
    """
    Возвращает список досок.

    :param request: Запрос.
    """
    boards = Board.objects.all()
    serializer = BoardSerializer(boards, many=True)
    return JsonResponse(serializer.data, safe=False)


@api_view(["GET"], )
@csrf_exempt
def get_all_threads(request, board_name, page) -> JsonResponse:
    """
    Возвращает список тредов с доски.
    Каждый объект треда содержит в себе ОП-пост и три последних поста.

    :param request: Запрос.
    :param board_name: Короткое имя доски.
    :param page: Страница.
    :raise Http404: Если доска не найдена.
    """
    threads = Thread.objects.filter(board__board_name=board_name)[
              page * THREADS_PER_PAGE: (page + 1) * THREADS_PER_PAGE]
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
def get_thread(request, board_name, thread_id) -> JsonResponse:
    """
    Возвращает тред со списком постов.

    :param request: Запрос.
    :param board_name: Короткое имя доски.
    :param thread_id: Номер треда.
    :raise Http404: Если тред не найден.
    """
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
def create_thread(request, board_name) -> JsonResponse:
    """
    Создает тред.
    Обязательно должен быть хотя бы один медиа-файл.

    :param request: Запрос с JSON поста.
    :param board_name: Короткое имя доски, где нужно создать тред.
    :raise Http404: Если доска не найдена.
    """
    return create_post_or_thread(request, board_name)


@api_view(["GET"], )
@csrf_exempt
def get_post(request, board_name, post_id) -> JsonResponse:
    """
    Получает один пост.

    :param request: Запрос.
    :param board_name: Короткое имя доски.
    :param post_id: Номер поста.
    :raise Http404: Если пост не найден.
    """
    post = get_object_or_404(Post, post_id=post_id, thread__board__board_name=board_name)
    serializer = PostSerializer(post)
    return JsonResponse(serializer.data, safe=False)


@api_view(["POST"], )
@csrf_exempt
def create_post(request, board_name, thread_id) -> JsonResponse:
    """
    Создает пост в треде.

    :param request: Запрос с JSON поста.
    :param board_name: Короткое имя доски.
    :param thread_id: Номер треда.
    :raise Http404: Если доска или тред не найдены.
    """
    return create_post_or_thread(request, board_name, thread_id)


@api_view(["GET"], )
@csrf_exempt
def get_file(request, file_hash) -> JsonResponse:
    """
    Получает информацию о файле вместе с прямыми ссылками на эскиз и контент.

    :param request: Запрос.
    :param file_hash: SHA512 хэш файла.
    :raise Http404: Если файл не найден.
    """
    file = get_object_or_404(File, hash=file_hash)
    serializer = FileSerializer(file)
    return JsonResponse(serializer.data, safe=False)


@csrf_exempt
def upload_file(request, board_name) -> Union[JsonResponse, MethodNotAllowed]:
    """
    Загружает файл на сервер.
    Файл хэшируется, с него читаются метаданные, для него создается эскиз,
    эскиз и контент грузяться на Amazon S3.

    :param request: Запрос с файлами (до четырех).
    :param board_name: Имя целевой доски для постинга файла (у каждой доски свое ограничение на размер).
    :return: Массив с именами фалов и результатом загрузки.
    :raise Http404: Если доска не найдена.
    """
    if request.method != 'POST':
        return MethodNotAllowed(request.method)

    result = []

    max_file_size = get_object_or_404(Board, board_name=board_name).max_file_size * 1024
    for filename, file in request.FILES.items():  # TODO: limit files count to 4
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

        fformat = filetype.guess(data)
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
