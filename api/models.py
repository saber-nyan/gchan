"""
Base imageboard models.
"""
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

from enum import Enum

from django.db import models
from django.utils import timezone


# noinspection PyUnusedLocal
def content_fname(model, fname):
    return f'c_{model.hash}'


# noinspection PyUnusedLocal
def preview_fname(model, fname):
    return f'p_{model.hash}'


class File(models.Model):
    class Meta:
        ordering = ['-created_at', '-modified_at', 'filename', ]

    class FileTypeEnum(Enum):
        JPEG = 'jpeg'
        PNG = 'png'
        GIF = 'gif'
        WEBM = 'webm'
        WEBP = 'webp'

    hash = models.CharField('SHA512', max_length=128, primary_key=True)
    filename = models.CharField('file name', max_length=256)
    width = models.PositiveIntegerField('media width')
    height = models.PositiveIntegerField('media height')
    size = models.PositiveIntegerField('file size')

    content = models.FileField('file content', upload_to=content_fname, max_length=256)
    preview_content = models.FileField('preview content', upload_to=preview_fname, max_length=256)

    thumbnailWidth = models.PositiveIntegerField('file width (thumbnail)')
    thumbnailHeight = models.PositiveIntegerField('file height (thumbnail)')
    filetype = models.CharField('file type', max_length=4,
                                choices=[(tag.name, tag.value) for tag in FileTypeEnum])

    created_at = models.DateTimeField('created at', editable=False)
    modified_at = models.DateTimeField('modified at', blank=True, editable=False)

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        if not self.created_at:
            self.created_at = timezone.now()
        self.modified_at = timezone.now()
        return super().save(force_insert, force_update, using, update_fields)

    def __str__(self):
        return f'{self.filename} <{self.hash}> {self.width}x{self.height}'


class Post(models.Model):
    class Meta:
        ordering = ['post_id', ]

    thread = models.ForeignKey('Thread', on_delete=models.CASCADE, related_name='posts',
                               verbose_name='thread', null=False, blank=False)

    post_id = models.PositiveIntegerField('post ID')
    banned = models.BooleanField('banned')
    warned = models.BooleanField('warned')
    text = models.TextField('text')
    email = models.CharField('email', max_length=64, blank=True)
    name = models.CharField('name', max_length=64, blank=True)
    subject = models.CharField('subject', max_length=64, blank=True)
    trip_code = models.CharField('tripcode', max_length=64, blank=True)
    op = models.BooleanField('OP mark')

    files = models.ManyToManyField(File, verbose_name='files', blank=True)

    created_at = models.DateTimeField('created at', editable=False)
    modified_at = models.DateTimeField('modified at', blank=True, editable=False)

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        if not self.created_at:
            self.created_at = timezone.now()
        self.modified_at = timezone.now()
        return super().save(force_insert, force_update, using, update_fields)

    def __str__(self):
        return f'>>{self.post_id} from "{self.name}"'


class Thread(models.Model):
    board = models.ForeignKey('Board', on_delete=models.CASCADE, related_name='threads',
                              verbose_name='board', null=False, blank=False)

    def __str__(self):
        return f'#{self.pk} ({self.posts.first()})'


class Board(models.Model):
    board_name = models.CharField('name', max_length=10)
    description = models.CharField('description', max_length=100)
    pages = models.PositiveIntegerField('page count')
    bump_limit = models.PositiveIntegerField('bump limit')
    default_name = models.CharField('default name', max_length=64)
    max_file_size = models.PositiveIntegerField('Maximum file size (in KB)')
    max_text_size = models.PositiveIntegerField('Maximum text size (in symbols)')

    created_at = models.DateTimeField('created at', editable=False)
    modified_at = models.DateTimeField('modified at', blank=True, editable=False)

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        if not self.created_at:
            self.created_at = timezone.now()
        self.modified_at = timezone.now()
        return super().save(force_insert, force_update, using, update_fields)

    def __str__(self):
        return f'/{self.board_name}/ ({self.description})'
