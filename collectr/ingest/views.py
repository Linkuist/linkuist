from django.views.generic.list import ListView

from . import models


class LinkView(ListView):

    template_name = 'ingest/link_list.html'
    model = models.Link
    ordering = ['-processed_at']

    def get_queryset(self):
        queryset = super(LinkView, self).get_queryset()
        return queryset.select_related(
            'link', 'sharer', 'sharer__media'
        ).filter(
            processed_at__isnull=False,
            metadata__user=self.request.user,
        )
