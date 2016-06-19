# python
from datetime import datetime
from dateutil.relativedelta import relativedelta

# django
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.utils.decorators import method_decorator
from django.views.generic import ListView

# collector
from source.models import LinkSum, Collection, Source


def home(request, template="webfront/home.html"):
    data = {
    }
    if request.user.is_authenticated():
        return redirect("webfront:collection")
    return render(request, template, data)


def search(request, template="webfront/collection.html"):
    data = {}
    querystring = request.GET.get('query')
    if not querystring:
        messages.error(request, u"Please enter a valid search term")
        return redirect('webfront:home')
    querystring = querystring.replace(' ', ' & ')

    links = LinkSum.objects.raw(
        """SELECT DISTINCT "source_linksum"."id", "source_linksum"."url_id", "source_linksum"."read", "source_linksum"."recommanded", "source_linksum"."collection_id", "source_linksum"."inserted_at", "source_linksum"."user_id"
           FROM source_linksum
           INNER JOIN source_url ON
              (source_linksum.url_id = source_url.id)
           AND
              to_tsvector('english', source_url.content) @@ to_tsquery('english', %s)
           AND "source_linksum"."user_id" = %s
           ORDER BY "source_linksum"."inserted_at" DESC;
         """, [querystring, request.user.id])

    data = {
        'links': links,
        'query': querystring,
        'collections': Collection.objects.filter(Q(user__id=request.user.id) | Q(user__isnull=True)),
        'sources': Source.objects.all(),
    }
    return render(request, template, data)


def get_display_paginate_item(paginator, page, adjacent_pages=5):
    """Alternate list of pages for paginated view.

    Prepares a compact list of pages including first and last page as well as
    a `adjacent_pages` number of pages around current `page`.
    """
    total_page = paginator.num_pages

    # Not enough pages
    if total_page <= adjacent_pages:
        page_range = paginator.page_range

    # first pages
    elif page <= 2 * (adjacent_pages / 2):
        page_range = range(1, adjacent_pages + 1)
        page_range.extend(['...', total_page])

    # between
    elif page <= total_page - 2 * (adjacent_pages / 2) :
        page_range = [1, '...']
        page_range.extend(range(
            page - adjacent_pages / 2,
            page + adjacent_pages / 2 + 1
        ))
        page_range.extend(['...', total_page])

    # last pages
    elif page > total_page - 2 * (adjacent_pages / 2):
        page_range = [1, '...']
        page_range.extend(range(
            total_page - adjacent_pages + 1,
            total_page + 1
        ))

    else:
        page_range = []

    return page_range


class BaseLinkSumView(ListView):
    """Basic view listing `LinkSum` objects."""

    template_name = 'webfront/collection.html'
    context_object_name = 'links'
    model = LinkSum
    ordering = ['-pk']
    paginate_by = 42

    def get_queryset(self):
        queryset = super(BaseLinkSumView, self).get_queryset()

        self.user_collections = Collection.objects.filter(
            Q(user__id=self.request.user.id) | Q(user__isnull=True)
        )

        return queryset \
            .filter(user=self.request.user) \
            .filter(hidden=False) \
            .select_related('authors')

    def get_context_data(self, **kwargs):
        # TODO: handle filter on read/unread/all
        context = {
            'collections': self.user_collections,
            'sources': Source.objects.all(),
        }
        context.update(kwargs)

        # Ask parent about pagination context
        context = super(BaseLinkSumView, self).get_context_data(**context)

        # Insert our custom compact pagination
        context.update({'page_range': get_display_paginate_item(
            context['paginator'], context['page_obj']
        )})
        return context

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(BaseLinkSumView, self).dispatch(*args, **kwargs)


class CollectionMixin(object):
    """Add per-collection filtering."""

    def get_queryset(self):
        queryset = super(CollectionMixin, self).get_queryset()

        collection = self.kwargs.get('collection', 'unread')
        if collection == 'unread':
            collection = 'all'

        return queryset.filter(
            collection=self.user_collections.get(name__iexact=collection)
        )


class DateView(CollectionMixin, BaseLinkSumView):

    ordering = ['-recommanded']

    def get_queryset(self):
        queryset = super(DateView, self).get_queryset()

        now = datetime.now()
        today = datetime(now.year, now.month, now.day)
        period_start, period_end = {
            'today': (today, now),
            'yesterday': (today + relativedelta(days=-1), today),
            'this_week': (today + relativedelta(weeks=-1, weekday=0), now),
            'last_week': (today + relativedelta(weeks=-2, weekday=0),
                          today + relativedelta(weeks=-1, weekday=0)),
            'this_month': (today + relativedelta(day=1), now),
            'last_month': (today + relativedelta(day=1, months=-1),
                           today + relativedelta(day=1)),
        }[self.kwargs.get('period', 'today')]

        return queryset.filter(inserted_at__range=(period_start, period_end))


class SourceView(BaseLinkSumView):

    def get_queryset(self):
        queryset = super(SourceView, self).get_queryset()
        return queryset.filter(
            sources__slug=self.kwargs.get('source'),
        )


class CollectionView(CollectionMixin, BaseLinkSumView):
    pass


class CollectionTagView(BaseLinkSumView):

    def get_queryset(self):
        queryset = super(CollectionTagView, self).get_queryset()
        return queryset.filter(
            url__tags__name=self.kwargs.get('tag'),
        )


class CollectionUserView(BaseLinkSumView):

    def get_queryset(self):
        queryset = super(CollectionUserView, self).get_queryset()
        return queryset.filter(
            authors__name=self.kwargs.get('user'),
            authors__source=self.kwargs.get('source'),
        )


@login_required
def ajax_hide_linksum(request, linksum_id):
    if not request.is_ajax():
        return HttpResponse(status_code=400)

    link = get_object_or_404(LinkSum, pk=linksum_id, user_id=request.user.pk)
    link.hidden = True
    link.save()
