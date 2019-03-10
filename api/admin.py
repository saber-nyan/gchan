from django.contrib import admin

from api.models import File, Post, Thread


def resolution(obj):
    return f'{obj.width}x{obj.height}'


class FileMembershipInline(admin.StackedInline):
    model = Post.files.through


@admin.register(File)
class FileAdmin(admin.ModelAdmin):
    inlines = [
        FileMembershipInline,
    ]
    list_display = ('hash', 'filename', resolution, 'size', 'filetype', 'created_at', 'modified_at',)
    list_filter = ('filetype',)
    search_fields = ['hash', 'filename', ]
    save_on_top = True


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    inlines = [
        FileMembershipInline,
    ]
    list_display = ('post_id', 'banned', 'warned', 'email', 'name', 'created_at', 'modified_at',)
    list_filter = ('banned', 'warned', 'op',)
    search_fields = ['post_id', 'text', 'email', 'name', 'subject', 'trip_code', 'files__filename', 'files__hash']
    save_on_top = True


class PostInline(admin.StackedInline):
    model = Post


@admin.register(Thread)
class ThreadAdmin(admin.ModelAdmin):
    inlines = [
        PostInline,
    ]
    list_filter = ('posts__banned', 'posts__warned', 'posts__op',)
    search_fields = ['posts__post_id', 'posts__text', 'posts__email', 'posts__name', 'posts__subject',
                     'posts__trip_code', 'posts__files__filename', 'posts__files__hash']
