# python
from datetime import datetime

# django
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import HttpResponse
from django.shortcuts import redirect

# rq
from redis import Redis
from rq import Queue, Connection

from semantism.process import index_url


def secret_bookmark(request, username):
    url = request.GET.get('url')
    link_from = request.GET.get('from')
    source = request.GET.get('source')
    token = request.GET.get('token')

    if None in (url, link_from, source, token):
        return HttpResponse(status=400)

    try:
        user = User.objects.get(username=username, userprofile__token=token)
    except User.DoesNotExist:
        return HttpResponse(status=403)

    with Connection(Redis(**settings.RQ_DATABASE)):
        links_queue = Queue('link_indexing')
        links_queue.enqueue_call(func=index_url,
            args=(url, user.id, datetime.now(), link_from, source), timeout=60
        )

    return HttpResponse(status=201)
