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

from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view
from rest_framework.generics import get_object_or_404

from api.models import Post, File, Thread, Board
from api.serializers import PostSerializer, ThreadSerializer, BoardSerializer


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
    # TODO: hide nested posts from list
    serializer = ThreadSerializer(threads, many=True)
    return JsonResponse(serializer.data, safe=False)


@api_view(["GET"], )
@csrf_exempt
def get_thread(request, board_name, thread_id):
    thread = get_object_or_404(Thread, board__board_name=board_name, posts__id=thread_id)
    serializer = ThreadSerializer(thread)
    # serializer.
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
