# python
from datetime import datetime
from dateutil.relativedelta import relativedelta

# django
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, EmptyPage, InvalidPage
from django.db.models import Q
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse

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


def get_display_paginate_item(paginator, page, max_paginated=5):
    """Prints nicely the range of paginating"""
    
    total_page = paginator.num_pages
    page_range = []

    # Not enough pages
    if total_page <= max_paginated:
        page_range = paginator.page_range

    # page starting
    elif page <= max_paginated:
        page_range = range(1, max_paginated)
        page_range.append('...')
        page_range.extend(range(total_page - max_paginated, max_paginated + 1))

    # between
    elif page < total_page:
        page_range.append(1)
        page_range.append('...')
        page_range.extend(range(page - (max_paginated / 2), page + max_paginated / 2))
        page_range.append('...')
        page_range.append(total_page)

    # final
    elif page >= total_page - max_paginated:
        page_range.append(1)
        page_range.append('...')
        page_range.extend(range(total_page - max_paginated, total_page + 1))

    return page_range


@login_required
def links_today(request, period, collection=None,
                template="webfront/collection.html"):
    show_read = True

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
    }[period]

    if collection == "unread" or not collection:
#        show_unread = False
        collection = "all"
    qs = LinkSum.objects.select_related('authors')\
                        .filter(hidden=False)\
                        .filter(user__id=request.user.id)\
                        .filter(inserted_at__range=(period_start, period_end))\
                        .order_by('-recommanded')
    if not show_read:
        qs.filter(read=False)

    if collection:
        collection = Collection.objects.filter(Q(user__id=request.user.id) | Q(user__isnull=True))\
                                       .get(name__iexact=collection)
        qs = qs.filter(collection__id=collection.id)

    paginator = Paginator(qs, 42)
    try:
        page = int(request.GET.get('page', '1'))
    except ValueError:
        page = 1

    try:
        links = paginator.page(page)
    except (EmptyPage, InvalidPage):
        links = paginator.page(paginator.num_pages)

    page_range = get_display_paginate_item(paginator, page)
    paginator = links
    links = links.object_list
    data = {
        'unread_count': links.count(),
        'paginator': paginator,
        'links': links,
        'collections': Collection.objects.filter(Q(user__id=request.user.id) | Q(user__isnull=True)),
        'sources': Source.objects.all(),
        'page_range': page_range,
    }

    return render(request, template, data)


@login_required
def collection(request, collection=None, template="webfront/collection.html"):
    show_read = True
    if collection == "unread" or not collection:
#        show_unread = False
        collection = "all"
    collection = Collection.objects.filter(Q(user__id=request.user.id) | Q(user__isnull=True))\
                                   .get(name__iexact=collection)
    qs = LinkSum.objects.select_related('authors')\
                        .filter(user__id=request.user.id)\
                        .filter(hidden=False)\
                        .filter(collection__id=collection.id)\
                        .order_by('-pk')
    if not show_read:
        qs.filter(read=False)

    paginator = Paginator(qs, 42)
    try:
        page = int(request.GET.get('page', '1'))
    except ValueError:
        page = 1

    try:
        links = paginator.page(page)
    except (EmptyPage, InvalidPage):
        links = paginator.page(paginator.num_pages)

    page_range = get_display_paginate_item(paginator, page)
    paginator = links
    links = links.object_list
    data = {
        'unread_count': links.count(),
        'paginator': paginator,
        'links': links,
        'collections': Collection.objects.filter(Q(user__id=request.user.id) | Q(user__isnull=True)),
        'sources': Source.objects.all(),
        'page_range': page_range,
    }

    return render(request, template, data)


@login_required
def collection_source(request, source, template="webfront/collection.html"):
    links = LinkSum.objects.select_related('authors')\
                           .filter(user__id=request.user.id)\
                           .filter(sources__slug=source)\
                           .filter(hidden=False)\
                           .order_by('-pk')[:100]
    data = {
        'unread_count': links.count(),
        'links': links,
        'collections': Collection.objects.filter(Q(user__id=request.user.id) | Q(user__isnull=True)),
        'sources': Source.objects.all(),
    }

    return render(request, template, data)


@login_required
def collection_tag(request, tag, template="webfront/collection.html"):
    links = LinkSum.objects.select_related('authors')\
                           .filter(user__id=request.user.id)\
                           .filter(hidden=False)\
                           .filter(url__tags__name=tag)\
                           .order_by('-pk')[:100]
    data = {
        'unread_count': links.count(),
        'links': links,
        'sources': Source.objects.all(),
        'collections': Collection.objects.filter(Q(user__id=request.user.id) | Q(user__isnull=True)),
    }

    return render(request, template, data)


@login_required
def collection_user(request, user, source, template="webfront/collection.html"):
    show_read = True
    qs = LinkSum.objects.select_related('authors')\
                        .distinct()\
                        .filter(user__id=request.user.id)\
                        .filter(authors__name=user)\
                        .filter(authors__source=source)\
                        .filter(hidden=False)\
                        .order_by('-pk')
    if not show_read:
        qs.filter(read=False)

    paginator = Paginator(qs, 42)
    try:
        page = int(request.GET.get('page', '1'))
    except ValueError:
        page = 1

    try:
        links = paginator.page(page)
    except (EmptyPage, InvalidPage):
        links = paginator.page(paginator.num_pages)

    page_range = get_display_paginate_item(paginator, page)
    paginator = links
    links = links.object_list
    data = {
        'unread_count': links.count(),
        'paginator': paginator,
        'links': links,
        'collections': Collection.objects.filter(Q(user__id=request.user.id) | Q(user__isnull=True)),
        'sources': Source.objects.all(),
        'page_range': page_range,
    }

    return render(request, template, data)


@login_required
def ajax_hide_linksum(request, linksum_id):
    if not request.is_ajax():
        return HttpResponse(status_code=400)

    link = get_object_or_404(LinkSum, pk=linksum_id, user_id=request.user.pk)
    link.hidden = True
    link.save()
