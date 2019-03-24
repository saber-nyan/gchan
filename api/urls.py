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

from django.urls import path

from api import views as v

urlpatterns = [
    path('board/', v.get_all_boards, name='get-all-boards'),
    path('board/<str:board_name>/<int:page>/', v.get_all_threads, name='get-all-threads'),

    path('board/<str:board_name>/thread/<int:thread_id>/', v.get_thread, name='get-thread'),
    path('board/<str:board_name>/thread/', v.create_thread, name='create-thread'),

    path('board/<str:board_name>/thread/<int:thread_id>/post/<int:post_id>/', v.get_post, name='get-post'),
    path('board/<str:board_name>/thread/<int:thread_id>/post/', v.create_post, name='create-post'),

    path('file/<str:file_hash>/', v.get_file, name='get-file'),
    path('file/thumbnail/<str:file_hash>/', v.get_thumbnail, name='get-thumbnail'),
    path('board/<str:board_name>/file/', v.upload_file, name='upload-file'),
]
