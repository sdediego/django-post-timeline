from django import forms
from django.utils import timezone

from .caches import cache_bust
from .models import Comment, Post, Timeline

# Create your forms here.

class CommentForm(forms.ModelForm):

    class Meta:
        model = Comment
        fields = [
            'text',
        ]
        labes = {
            'text': 'Text',
        }
        widgets = {
            'text': forms.TextInput(),
        }

    def save(self, *args, **kwargs):
        """
        Save method for post comments.
        """
        user = kwargs.get('user')
        if user.is_authenticated():
            comment = super(CommentForm, self).save(commit=False)
            comment.post = kwargs.get('post')
            comment.author = user
            comment.save()
            cache_bust([('comments', comment.post.pk)])
            return comment
        return False


class PostForm(forms.ModelForm):

    class Meta:
        model = Post
        fields = [
            'author',
            'title',
            'body',
            'image',
        ]
        labels = {
            'author': 'Author',
            'title': 'Title',
            'body': 'Text',
            'image': 'Image',
        }
        widgets = {
            'author': forms.TextInput(),
            'title': forms.TextInput(),
            'body': forms.Textarea(),
        }

    def save(self, *args, **kwargs):
        """
        Save method for post.
        Assign user to post author if not assigned before and
        update timestamp with last time post edition.
        """
        user = kwargs.get('user')
        if user.is_authenticated():
            post = super(PostForm, self).save(commit=False)
            post_author = self.cleaned_data.get('author')
            updated = kwargs.get('updated')
            if post_author != user:
                post.author = user
            if updated:
                post.last_updated = timezone.now()
            post.save()
            if not updated:
                Timeline.objects.add_to_timeline(instance=post, user=user)
            cache_bust([('posts_timeline', user.pk)])
            return post
        return False
