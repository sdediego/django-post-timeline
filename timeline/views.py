from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.shortcuts import get_list_or_404, get_object_or_404, redirect, render
from django.views.decorators.http import require_http_methods

from .forms import CommentForm, PostForm
from .models import Comment, Post, Timeline

# Create your views here.

@login_required(login_url='/login/')
def add_comment_to_post(request, post_id, template='post_comment_add.html'):
    post = get_object_or_404(Post, pk=post_id)
    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            form.save(post=post, user=request.user)
            return redirect('timeline:read_post', post_id=post.pk)
    form = CommentForm(instance=post)
    return render(request, template, {'form': form, 'post': post})


@login_required(login_url='/login/')
def add_post(request, template='post_add_edit.html'):
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            form.save(user=request.user, updated=False)
            return redirect('timeline:timeline_post')
    form = PostForm()
    return render(request, template, {'form': form})


@login_required(login_url='/login/')
def comment_approve_or_disapprove(request, comment_id, status):
    comment = get_object_or_404(Comment, pk=comment_id)
    comment.change_approval(status)
    return redirect('timeline:read_post', post_id=comment.post.pk)


@login_required(login_url='/login/')
def delete_comment_from_post(request, comment_id, template='post_comment_delete.html'):
    comment = get_object_or_404(Comment, pk=comment_id)
    if request.method == 'POST':
        post = comment.delete(user=request.user)
        return redirect('timeline:read_post', post_id=post.pk)
    return render(request, template, {'comment': comment})


@login_required(login_url='/login/')
def delete_post(request, post_id, template='post_delete.html'):
    post = get_object_or_404(Post, pk=post_id)
    if request.method == 'POST':
        post.delete(user=request.user)
        return redirect('timeline:timeline_post')
    return render(request, template, {'post': post})


@login_required(login_url='/login/')
def edit_post(request, post_id, template='post_add_edit.html'):
    post = get_object_or_404(Post, pk=post_id)
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES, instance=post)
        if form.is_valid():
            form.save(user=request.user, updated=True)
            return redirect('timeline:read_post', post_id=post.pk)
    form = PostForm(instance=post)
    return render(request, template, {'form': form, 'post': post})


@login_required(login_url='/login/')
@require_http_methods(['GET'])
def read_post(request, post_id, template='post_read.html'):
    post = get_object_or_404(Post, pk=post_id)
    return render(request, template, {'post': post})


@login_required(login_url='/login/')
@require_http_methods(['GET'])
def show_posts_timeline(request, template='post_timeline.html'):
    timeline = Timeline.objects.get_timeline(model='post', user=request.user)
    posts = Post.objects.get_posts_timeline(user=request.user, timeline=timeline)
    return render(request, template, {'posts': posts})
