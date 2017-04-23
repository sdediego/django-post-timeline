from django import template

from .models import Comment

# Create your template tags here.

register = template.Library()


@register.simple_tag
def post_comments(post):
    """
    Simple tag to retrieve all comments.
    """
    comments = Comment.objects.comments(post=post)
    return comments


@register.simple_tag
def post_comments_count(post):
    """
    Simple tag to display the total count of comments for one post.
    """
    comments_count = Comment.objects.comments_count(post=post)
    return comments_count
