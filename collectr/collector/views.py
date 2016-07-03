# python
from datetime import datetime

# django
from django.conf import settings
from django.contrib.auth.models import User
from django.http import HttpResponse
from django.template.response import TemplateResponse
from django.views.generic import TemplateView

# rq
from redis import Redis
from rq import Queue, Connection

from semantism.process import index_url


class AcceptTemplateResponse(TemplateResponse):
    """`TemplateResponse` that returns with 202 Accept status code."""
    status_code = 202


class SubmitBookmarkView(TemplateView):

    response_class = AcceptTemplateResponse
    template_name = 'collector/bookmark_submit.html'

    def get(self, request, *args, **kwargs):
        url = request.GET.get('url')
        link_from = request.GET.get('from')
        source = request.GET.get('source')
        token = request.GET.get('token')

        if None in (url, link_from, source, token):
            return HttpResponse(status=400)

        try:
            user = User.objects.get(username=kwargs['username'],
                                    userprofile__token=token)
        except User.DoesNotExist:
            return HttpResponse(status=403)

        with Connection(Redis(**settings.RQ_DATABASE)):
            links_queue = Queue('link_indexing')
            links_queue.enqueue_call(
                func=index_url,
                args=(url, user.id, datetime.now(), link_from, source),
                timeout=60
            )

        return super(SubmitBookmarkView, self).get(request, *args, **kwargs)

