# Generated by Django 2.1.7 on 2019-03-27 12:37

import api.models
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Board',
            fields=[
                ('board_name', models.CharField(max_length=10, primary_key=True, serialize=False, verbose_name='name')),
                ('description', models.CharField(max_length=100, verbose_name='description')),
                ('pages', models.PositiveIntegerField(verbose_name='page count')),
                ('bump_limit', models.PositiveIntegerField(verbose_name='bump limit')),
                ('default_name', models.CharField(max_length=64, verbose_name='default name')),
                ('max_file_size', models.PositiveIntegerField(verbose_name='maximum file size (in KB)')),
                ('max_text_size', models.PositiveIntegerField(verbose_name='maximum text size (in symbols)')),
                ('created_at', models.DateTimeField(editable=False, verbose_name='created at')),
                ('modified_at', models.DateTimeField(blank=True, editable=False, verbose_name='modified at')),
            ],
        ),
        migrations.CreateModel(
            name='File',
            fields=[
                ('hash', models.CharField(max_length=128, primary_key=True, serialize=False, verbose_name='SHA512')),
                ('filename', models.CharField(max_length=256, verbose_name='file name')),
                ('width', models.PositiveIntegerField(verbose_name='media width')),
                ('height', models.PositiveIntegerField(verbose_name='media height')),
                ('size', models.PositiveIntegerField(verbose_name='file size')),
                ('content', models.FileField(max_length=256, upload_to=api.models.content_fname, verbose_name='file content')),
                ('preview_content', models.FileField(max_length=256, upload_to=api.models.preview_fname, verbose_name='preview content')),
                ('thumbnailWidth', models.PositiveIntegerField(verbose_name='file width (thumbnail)')),
                ('thumbnailHeight', models.PositiveIntegerField(verbose_name='file height (thumbnail)')),
                ('filetype', models.CharField(choices=[('JPEG', 'jpg'), ('PNG', 'png'), ('GIF', 'gif'), ('WEBM', 'webm'), ('WEBP', 'webp')], max_length=4, verbose_name='file type')),
                ('created_at', models.DateTimeField(editable=False, verbose_name='created at')),
                ('modified_at', models.DateTimeField(blank=True, editable=False, verbose_name='modified at')),
            ],
            options={
                'ordering': ['-created_at', '-modified_at', 'filename'],
            },
        ),
        migrations.CreateModel(
            name='Post',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('post_id', models.PositiveIntegerField(verbose_name='post ID')),
                ('banned', models.BooleanField(verbose_name='banned')),
                ('warned', models.BooleanField(verbose_name='warned')),
                ('text', models.TextField(verbose_name='text')),
                ('email', models.CharField(blank=True, max_length=64, verbose_name='email')),
                ('name', models.CharField(blank=True, max_length=64, verbose_name='name')),
                ('subject', models.CharField(blank=True, max_length=64, verbose_name='subject')),
                ('trip_code', models.CharField(blank=True, max_length=64, verbose_name='tripcode')),
                ('op', models.BooleanField(verbose_name='OP mark')),
                ('created_at', models.DateTimeField(editable=False, verbose_name='created at')),
                ('modified_at', models.DateTimeField(blank=True, editable=False, verbose_name='modified at')),
                ('files', models.ManyToManyField(blank=True, to='api.File', verbose_name='files')),
            ],
            options={
                'ordering': ['post_id'],
            },
        ),
        migrations.CreateModel(
            name='Thread',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('pinned', models.BooleanField(verbose_name='always on top')),
                ('closed', models.BooleanField(verbose_name='closed')),
                ('board', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='threads', to='api.Board', verbose_name='board')),
            ],
            options={
                'ordering': ['-pinned'],
            },
        ),
        migrations.AddField(
            model_name='post',
            name='thread',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='posts', to='api.Thread', verbose_name='thread'),
        ),
    ]
