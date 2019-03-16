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

import logging

from django.core.exceptions import ValidationError
from django.http import JsonResponse, HttpResponse, Http404
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view
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
    threads = Thread.objects.filter(board__board_name=board_name)[page * per_page: (page + 1) * per_page]
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


@api_view(["POST"], )
@csrf_exempt
def upload_file(request):
    pass
