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
Описание моделей борды.
"""

from enum import Enum

from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone


# noinspection PyUnusedLocal
def content_fname(model, fname):
    """
    Имя файла из префикса ``c_`` и хэша.
    """
    return f'c_{model.hash}'


# noinspection PyUnusedLocal
def preview_fname(model, fname):
    """
    Имя файла из префикса ``p_`` и хэша.
    """
    return f'p_{model.hash}'


class File(models.Model):
    """
    Хранит в себе информацию о файле и прямую ссылку
    на превью и контент с Amazon S3.
    """

    class Meta:
        ordering = ['filename', ]
        verbose_name = 'файл'
        verbose_name_plural = 'файлы'

    class FileTypeEnum(Enum):
        """
        Список поддерживаемых типов файла.
        """
        JPEG = 'jpg'
        PNG = 'png'
        GIF = 'gif'
        WEBM = 'webm'
        WEBP = 'webp'

        @classmethod
        def has_value(cls, value):
            """
            Enum содержит в себе указанный элемент?
            """
            return any(value == item.value for item in cls)

        @classmethod
        def list_values(cls):
            """
            Вохвращает список значений.
            """
            return [item.value for item in cls]

    hash = models.CharField('SHA512', max_length=128, primary_key=True)
    filename = models.CharField('имя', max_length=256)
    width = models.PositiveIntegerField('ширина медиа')
    height = models.PositiveIntegerField('высота медиа')
    size = models.PositiveIntegerField('размер')

    content = models.FileField('содержимое', upload_to=content_fname, max_length=256)
    preview_content = models.FileField('эскиз', upload_to=preview_fname, max_length=256)

    thumbnailWidth = models.PositiveIntegerField('ширина эскиза')
    thumbnailHeight = models.PositiveIntegerField('высота эскиза')
    filetype = models.CharField('тип', max_length=4,
                                choices=[(tag.name, tag.value) for tag in FileTypeEnum])

    created_at = models.DateTimeField('создан', editable=False)
    modified_at = models.DateTimeField('изменен', blank=True, editable=False)

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        """
        Указывает дату-время сохранения и изменения.
        """
        if not self.created_at:
            self.created_at = timezone.now()
        self.modified_at = timezone.now()
        return super().save(force_insert, force_update, using, update_fields)

    def __str__(self):
        return f'{self.filename} <{self.hash}> {self.width}x{self.height}'


class Post(models.Model):
    """
    Хранит в себе всю информацию о конкретном посте.
    """

    class Meta:
        ordering = ['post_id', ]
        verbose_name = 'пост'
        verbose_name_plural = 'посты'

    thread = models.ForeignKey('Thread', on_delete=models.CASCADE, related_name='posts',
                               verbose_name='тред', null=False, blank=False)

    post_id = models.PositiveIntegerField('ID')
    banned = models.BooleanField('забанен?', default=False)
    warned = models.BooleanField('предупрежден?', default=False)
    text = models.TextField('текст')
    email = models.CharField('почта', max_length=64, blank=True)
    name = models.CharField('имя', max_length=64, blank=True)
    subject = models.CharField('тема', max_length=64, blank=True)
    trip_code = models.CharField('трипкод', max_length=64, blank=True)
    op = models.BooleanField('ОП-флажок', default=False)

    files = models.ManyToManyField(File, verbose_name='файлы', blank=True)

    created_at = models.DateTimeField('создан', editable=False)
    modified_at = models.DateTimeField('изменен', blank=True, editable=False)

    def validate_unique(self, exclude=None):
        """
        Проверяет, нет ли на одной доске постов с одинаковыми ``post_id``.
        """
        if exclude is not None and 'thread' in exclude:
            return super().validate_unique(exclude)  # early return
        for post in Post.objects.all():
            if post.post_id == self.post_id and post.thread.board.board_name == self.thread.board.board_name:
                if post.pk == self.pk:
                    continue
                raise ValidationError({'post_id': ['Post ID must be unique per board', ], })
        return super().validate_unique(exclude)

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        """
        Указывает дату-время сохранения и изменения.
        """
        if not self.created_at:
            self.created_at = timezone.now()
        self.modified_at = timezone.now()
        # self.validate_unique()
        return super().save(force_insert, force_update, using, update_fields)

    def __str__(self):
        return f'>>{self.post_id} from "{self.name}"'


class Thread(models.Model):
    """
    Хранит в себе некоторые свойства треда и список постов (обратная связь).
    Первый элемент в списке — ОП-пост.
    """

    class Meta:
        ordering = ['-pinned', '-last_bump_time']
        verbose_name = 'тред'
        verbose_name_plural = 'треды'

    pinned = models.BooleanField('прилеплен')
    closed = models.BooleanField('закрыт')
    board = models.ForeignKey('Board', on_delete=models.CASCADE, related_name='threads',
                              verbose_name='доска', null=False, blank=False)
    last_bump_time = models.DateTimeField('последний бамп', default=timezone.now)

    def __str__(self):
        return f'#{self.pk} ({self.posts.first()})'


class Board(models.Model):
    """
    Хранит в себе некоторые свойства доски и список тредов (обратная связь).
    """

    class Meta:
        verbose_name = 'доска'
        verbose_name_plural = 'доски'

    board_name = models.CharField('название', primary_key=True, max_length=10)
    description = models.CharField('описание', max_length=100)
    pages = models.PositiveIntegerField('кол-во страниц')
    bump_limit = models.PositiveIntegerField('бамплимит')
    default_name = models.CharField('имя по умолчанию', max_length=64)
    max_file_size = models.PositiveIntegerField('максимальный размер файла (в КБ)')
    max_text_size = models.PositiveIntegerField('максимальное количество символов')

    closed = models.BooleanField('закрыта?')

    created_at = models.DateTimeField('создана', editable=False)
    modified_at = models.DateTimeField('изменена', blank=True, editable=False)

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        """
        Указывает дату-время сохранения и изменения.
        """
        if not self.created_at:
            self.created_at = timezone.now()
        self.modified_at = timezone.now()
        return super().save(force_insert, force_update, using, update_fields)

    def __str__(self):
        return f'/{self.board_name}/ ({self.description})'
