"""
Base imageboard models.
"""
import os
from enum import Enum

from django.db import models
from django.utils import timezone

from gchan import settings


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
    path = models.FilePathField('file path (fullres)', path=os.path.join(settings.USER_FILE_PATH, 'fullres'),
                                max_length=500)
    thumbnailPath = models.FilePathField('file path (thumbnail)',
                                         path=os.path.join(settings.USER_FILE_PATH, 'thumb'), max_length=500)
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
    def __str__(self):
        return f'#{self.pk} ({self.posts.first()})'
