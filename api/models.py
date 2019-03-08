"""
Base imageboard models.
"""
import os
from enum import Enum

from django.db import models

from gchan import settings


class File(models.Model):
    class FileTypeEnum(Enum):
        JPEG = 'jpeg'
        PNG = 'png'
        GIF = 'gif'
        WEBM = 'webm'
        WEBP = 'webp'

    filename = models.CharField('Media file name', max_length=256)
    width = models.PositiveIntegerField('Media file width')
    height = models.PositiveIntegerField('Media file height')
    size = models.PositiveIntegerField('Media file size')
    path = models.FilePathField('Media file path (fullres)', path=os.path.join(settings.USER_FILE_PATH, 'fullres'),
                                max_length=500)
    thumbnailPath = models.FilePathField('Media file path (thumbnail)',
                                         path=os.path.join(settings.USER_FILE_PATH, 'thumb'), max_length=500)
    thumbnailWidth = models.PositiveIntegerField('Media file width (thumbnail)')
    thumbnailHeight = models.PositiveIntegerField('Media file height (thumbnail)')
    filetype = models.CharField('Media file type', max_length=4,
                                choices=[(tag.name, tag.value) for tag in FileTypeEnum])
    hash = models.CharField('SHA512 file hash', max_length=128)
