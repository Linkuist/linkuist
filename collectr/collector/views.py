# python
from datetime import datetime

# django
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import HttpResponse
from django.shortcuts import redirect

# rq
from redis import Redis
from rq import use_connection, Queue

from semantism.process import index_url

links_queue = Queue('link_indexing', connection=Redis('127.0.0.1', port=6379))

@login_required
def bookmark(request, template_name="collector/bookmark.html"):
    url = request.GET.get('url')
    user = request.user
    links_queue.enqueue(index_url, url, request.user.id, datetime.now(), request.user.username, "bookmarks")
    return redirect(url)


def secret_bookmark(request, username):
    url = request.GET.get('url')
    link_from = request.GET.get('from')
    source = request.GET.get('source')

    if not url or not link_from or not source:
        return HttpResponse(status=404)

    try:
        user = User.objects.get(username=username)
    except User.DoesNotExist:
        return HttpResponse(status=403)

    links_queue.enqueue(index_url, url, user.id, datetime.now(), link_from, source)

    return HttpResponse(status=201)

