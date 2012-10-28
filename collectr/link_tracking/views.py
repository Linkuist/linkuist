# Create your views here.
from django.shortcuts import redirect

from source.models import LinkSum, UrlViews

def track_link(request, link_id):
    link = LinkSum.objects.select_related('url__link').get(pk=link_id)
    link.read = True
    link.save()

    try:
        uv = UrlViews.objects.get(url__linksum__pk=link.pk)
        uv.count += 1
        uv.save()
    except UrlViews.DoesNotExist:
        url = link.url
        uv = UrlViews.objects.create(count=1)
        url.views = uv
        url.save()

    return redirect(link.url.link)
