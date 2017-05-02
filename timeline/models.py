import os

from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
from django.contrib.contenttypes.models import ContentType
from django.db import models, transaction
from django.urls import reverse
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _

from .caches import cache_bust
from .managers import CommentManager, PostManager, TimelineManager

# Create your models here.

def user_directory(instance, type_content):
    media_rel_path = '{user}/{type_content}/posts/'.format(user=instance.author, type_content=type_content)
    directory_abs_path = os.path.join(getattr(settings, 'MEDIA_ROOT', None), media_rel_path)
    if not os.path.exists(directory_abs_path):
        try:
            os.makedirs(directory_abs_path)
        except OSError:
            raise('Failure while creating media directory.')
    return directory_abs_path


def image_full_path(instance, filename):
    # Image will be uploaded to MEDIA_ROOT/<username>/images/posts/
    directory_abs_path = user_directory(instance, type_content='images')
    media_path = os.path.join(directory_abs_path, filename)
    return media_path


class Timeline(models.Model):
    """
    User timeline showing the posts ordered
    by date and time of creation.
    """
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
    )
    date = models.DateTimeField(
        _('Date'),
        editable=False,
    )
    # Below the mandatory fields for generic relation.
    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')

    objects = TimelineManager()

    class Meta:
        verbose_name = _('Timeline')
        verbose_name_plural = _('Timelines')

    def __str__(self):
        """
        Display a model instance.
        """
        return '{user}\'s timeline'.format(user=self.user.username)


class Post(models.Model):
    """
    Model for users to post media content to be
    shown in the timeline.
    """
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
    )
    title = models.CharField(
        _('Title'),
        max_length=100,
        blank=True,
        help_text=_('Post title.'),
        error_messages={'invalid': _('Please insert 100 character post title.')},
    )
    body = models.TextField(
        _('Body'),
        max_length=500,
        blank=False,
        help_text=_('Post main text.'),
        error_messages={'invalid': _('Please insert post content up to 500 characters.')},
    )
    image = models.ImageField(
        _('Image'),
        upload_to=image_full_path,
        blank=True,
        help_text=_('Image full path.'),
        error_messages={'invalid': _('Please choose a valid format image.')},
    )
    created = models.DateTimeField(
        _('Created'),
        default=timezone.now,
        editable=False,
    )
    last_updated = models.DateTimeField(
        _('Last updated'),
        null=True,
        blank=True,
        editable=True,
    )
    timeline = GenericRelation(
        Timeline,
        related_query_name='post',
    )

    objects = PostManager()

    class Meta:
        verbose_name = _('Post')
        verbose_name_plural = _('Posts')
        ordering = ('-created',)
        get_latest_by = 'created'

    def __str__(self):
        """
        Display a model instance.
        """
        return 'Post created by {author} on {date}: {title}'.format(
                author=self.author, date=self.created, title=self.title)

    def get_absolute_url(self):
        """
        Calculate the canonical URL for an object
        to refer to the object over HTTP.
        """
        reverse_url = reverse('timeline:read_post', kwargs={'post_id': self.pk})
        return reverse_url

    def has_media(self):
        """
        Check if post has media.
        """
        if self.image:
            return True
        return False

    def _handle_removed_media(self):
        """
        Remove media from filesystem.
        """
        if self.has_media():
            try:
                image = str(self.image)
                os.remove(image)
            except OSError:
                raise('Failure trying to remove image from filesystem.')
        return True

    @transaction.atomic
    def delete(self, user):
        """
        Method to delete content already posted.
        Handle image removal from filesystem prior to
        delete its path from database.
        """
        if user.is_authenticated() and self.author == user:
            if self._handle_removed_media():
                Timeline.objects.remove_from_timeline(instance=self, user=user)
                super(Post, self).delete()
                cache_bust([('posts_timeline', user.pk), ('comments', self.pk)])
                return True
        return False


class Comment(models.Model):
    """
    Model for users to comment on post content to be
    shown with in the timeline.
    """
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
    )
    text = models.TextField(
        _('Text'),
        max_length=500,
        blank=True,
        help_text=_('Comment text.'),
        error_messages={
            'invalid': _('Please insert comment text up to 500 characters.')
        },
    )
    created = models.DateTimeField(
        _('Created'),
        default=timezone.now,
        editable=False,
    )
    approved = models.BooleanField(
        _('Approved'),
        default=True,
    )

    objects = CommentManager()

    class Meta:
        verbose_name = _('Comment')
        verbose_name_plural = _('Comments')
        ordering = ('-created',)
        get_latest_by = 'created'

    def __str__(self):
        """
        Display a model instance.
        """
        return 'Autor: {user}.\nText: {text}'.format(user=self.author, text=self.text)

    @transaction.atomic
    def approve(self):
        """
        Approve a comment.
        """
        if not self.approved:
            self.approved = True
            self.save()
            cache_bust([('comments', self.post.pk)])
            return True

    @transaction.atomic
    def disapprove(self):
        """
        Disapprove a comment.
        """
        if self.approved:
            self.approved = False
            self.save()
            cache_bust([('comments', self.post.pk)])
            return True

    def change_approval(self, status):
        """
        Approve or disapprove a comment.
        """
        if status == 'approve':
            return self.approve()
        elif status == 'disapprove':
            return self.disapprove()

    @transaction.atomic
    def delete(self, user):
        """
        Remove comment from database.
        """
        if user.is_authenticated() and self.author == user:
            post = self.post
            super(Comment, self).delete()
            cache_bust([('comments', post.pk)])
            return post
        return False
