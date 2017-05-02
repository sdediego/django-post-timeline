import datetime

from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.core.cache import cache
from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.db import models
from django.db.models import Q
from django.utils import timezone

from .models import Follow
from .caches import cache_bust, make_key, make_key_many

# Create your managers here.

class CommentManager(models.Manager):
    """
    Comment model manager.
    """

    def comments(self, post):
        """
        Get all post comments.
        """
        key = make_key('comments', post.pk)
        comments = cache.get(key)
        if comments is None:
            comments = self.filter(post__pk=post.pk).order_by('-created')
            cache.set(key, comments)
        return comments

    def comments_count(self, post):
        """
        Return a count of all post comments.
        """
        count = self.comments(post).count()
        return count

    def approved_comments(self, post):
        """
        Get post approved comments.
        """
        key = make_key('approved_comments', post.pk)
        approved = cache.get(key)
        if approved is None:
            approved = self.filter(post__pk=post.pk, approved=True).order_by('-created')
            cache.set(key, approved)
        return approved

    def approved_comments_count(self, post):
        """
        Return a count of all post approved comments.
        """
        count = self.approved_comments(post).count()
        return count

    def disapproved_comments(self, post):
        """
        Get post disapproved comments.
        """
        key = make_key('disapproved_comments', post.pk)
        disapproved = cache.get(key)
        if disapproved is None:
            disapproved = self.filter(post__pk=post.pk, approved=False).order_by('-created')
            cache.set(key, disapproved)
        return disapproved

    def disapproved_comments_count(self, post):
        """
        Return a count of all post disapproved comments.
        """
        count = self.disapproved_comments(post).count()
        return count

    def delete_disapproved(self, post):
        """
        Remove disapproved comments for a post.
        """
        if user.is_authenticated() and user == post.author:
            disapproved = self.disapproved_comments(post)
            if disapproved:
                disapproved.delete()
                cache_bust([('disapproved_comments', post.pk)])
            return True
        return False


class PostManager(models.Manager):
    """
    Post model manager.
    """

    def get_posts_timeline(self, user, timeline):
        """
        Get the timeline of posts in reverse order
        of creation.
        """
        key = make_key('posts_timeline', user.pk)
        posts_timeline = cache.get(key)
        if posts_timeline is None:
            posts_timeline = self.filter(pk__in=timeline).order_by('-created')
            cache.set(key, posts_timeline)
        return posts_timeline

    def posts(self, user):
        """
        Return all user's posts.
        """
        key = make_key('posts', user.pk)
        posts = cache.get(key)
        if posts is None:
            posts = self.filter(author=user)
            cache.set(key, posts)
        return posts

    def post_count(self, user):
        """
        Return a count of one user's posts.
        """
        count = self.posts(user).count()
        return count


class TimelineManager(models.Manager):
    """
    Timeline model manager.
    """

    def add_to_timeline(self, instance, user):
        """
        Add instance to user's timeline when saving.
        """
        ctype = ContentType.objects.get_for_model(instance)
        timeline, created = self.get_or_create(content_type=ctype, object_id=instance.pk, user=user, date=instance.created)
        if created:
            cache_bust([('posts_timeline', user.pk)])
            return timeline
        return False

    def remove_from_timeline(self, instance, user):
        """
        Remove instance from user's timeline when deleting.
        """
        ctype = ContentType.objects.get_for_model(instance)
        try:
            timeline = self.get(content_type=ctype, object_id=instance.pk, user=user)
            timeline.delete()
            return True
        except self.model.DoesNotExist:
            raise ObjectDoesNotExist('Failure trying to delete {instance}'.format(instance=instance.title))

    def _is_installed_app(self, app):
        """
        Check if a concrete web application is
        installed in settings.INSTALLED_APPS.
        """
        installed_apps = getattr(settings, 'INSTALLED_APPS', None)
        if installed_apps is None:
            raise AttributeError('Error getting INSTALLED_APPS attribute.')
        if app in installed_apps:
            return True
        else:
            installed_apps_short = [apps_long.split('.')[-1] for apps_long in installed_apps]
            if app in installed_apps_short:
                return True
        return False

    def _get_query(self, model, user, last_days):
        """
        Construct the query.
        """
        ctype = ContentType.objects.get(model=model)
        authors_list = [user.pk]
        if self._is_installed_app('follow'):
            followees = Follow.objects.followees(user=user)
            followees_id = [followee.pk for followee in followees]
            authors_list.extend(followees_id)
        query = Q(content_type=ctype) & Q(user__pk__in=authors_list)
        if last_days is not None:
            time = timezone.now() - datetime.timedelta(days=last_days)
            query &= Q(date__gt=time)
        return query

    def get_timeline(self, model, user, last_days=None):
        """
        Construct the timeline for each user.
        User timeline is made of instances created by the user
        and his followees and contacts if any.
        Return instances id's.
        """
        key = make_key('timeline', user.pk)
        timeline = cache.get(key)
        if timeline is None:
            query = self._get_query(model, user, last_days)
            timeline = self.filter(query).values_list('object_id', flat=True)
            cache.set(key, timeline)
        return timeline
