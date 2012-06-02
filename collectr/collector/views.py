# python
from datetime import datetime

# django
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import HttpResponse
from django.shortcuts import redirect

# semantism
from semantism.tasks import TwitterStatus

@login_required
def bookmark(request, template_name="collector/bookmark.html"):
    url = request.GET.get('url')
    user = request.user
    t = TwitterStatus()
    t.apply_async(args=(url, request.user.id, datetime.now(), request.user.username, "bookmarks"))
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

    t = TwitterStatus()
    t.apply_async(args=(url, user.id, datetime.now(), link_from, source))

    return HttpResponse(status=201)


