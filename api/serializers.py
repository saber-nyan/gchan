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

from rest_framework import serializers

from api.models import Post, File, Thread, Board


class FileSerializer(serializers.ModelSerializer):
    class Meta:
        model = File
        exclude = ('modified_at',)


class PostSerializer(serializers.ModelSerializer):
    files = FileSerializer(many=True)

    class Meta:
        model = Post
        exclude = ('modified_at', 'thread', 'id',)
        depth = 1


class BoardSerializer(serializers.ModelSerializer):
    class Meta:
        model = Board
        exclude = ('modified_at', 'created_at',)
        depth = 1


class ThreadSerializer(serializers.ModelSerializer):
    posts = PostSerializer(many=True)
    board = BoardSerializer()

    @staticmethod
    def setup_eager_loading(queryset):
        """Perform necessary eager loading of data."""
        queryset = queryset.prefetch_related('posts', 'posts__files')
        return queryset

    class Meta:
        model = Thread
        exclude = ('id',)
        depth = 2
