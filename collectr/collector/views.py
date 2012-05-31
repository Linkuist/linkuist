# python
from datetime import datetime

# django
from django.contrib.auth.decorators import login_required
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
