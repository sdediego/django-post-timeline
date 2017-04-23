from django.conf.urls import url

from . import views

# Create your urls here.

urlpatterns = [
    url(
        regex=r'^$',
        view=views.show_posts_timeline,
        name='timeline_post',
    ),
    url(
        regex=r'^post/add/$',
        view=views.add_post,
        name='add_post',
    ),
    url(
        regex=r'^post/delete/(?P<post_id>\d+)$',
        view=views.delete_post,
        name='delete_post',
    ),
    url(
        regex=r'^post/edit/(?P<post_id>\d+)/$',
        view=views.edit_post,
        name='edit_post',
    ),
    url(
        regex=r'^post/read/(?P<post_id>\d+)/$',
        view=views.read_post,
        name='read_post',
    ),
    url(
        regex=r'^post/(?P<post_id>\d+)/comment/$',
        view=views.add_comment_to_post,
        name='add_comment',
    ),
    url(
        regex=r'^post/comment/(?P<comment_id>\d+)/(?P<status>\w{7,10})/$',
        view=views.comment_approve_or_disapprove,
        name='approval_comment',
    ),
    url(
        regex=r'^post/comment/(?P<comment_id>\d+)/delete/$',
        view=views.delete_comment_from_post,
        name='delete_comment',
    ),
]
