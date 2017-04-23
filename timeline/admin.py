from django.contrib import admin

from .models import Comment, Post, Timeline

# Register your models here.

class CommentAdmin(admin.ModelAdmin):
    model = Comment
    raw_id_fields = ('post', 'author')


class PostAdmin(admin.ModelAdmin):
    model = Post
    raw_id_fields = ('author',)


class TimelineAdmin(admin.ModelAdmin):
    model = Timeline
    raw_id_fields = ('user',)


admin.site.register(Comment, CommentAdmin)
admin.site.register(Post, PostAdmin)
admin.site.register(Timeline, TimelineAdmin)
