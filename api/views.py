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
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view
from rest_framework.generics import get_object_or_404

from api.models import Post
from api.serializers import PostSerializer


@api_view(["GET"], )
@csrf_exempt
def get_all_boards(request):
    pass


@api_view(["GET"], )
@csrf_exempt
def get_all_threads(request, board_name, page):
    pass


@api_view(["GET"], )
@csrf_exempt
def get_thread(request, board_name, thread_id):
    pass


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
    pass


@api_view(["GET"], )
@csrf_exempt
def get_thumbnail(request, file_hash):
    pass


@api_view(["POST"], )
@csrf_exempt
def upload_file(request):
    pass
