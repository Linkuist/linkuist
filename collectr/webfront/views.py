# python
from datetime import datetime, timedelta

# django
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger, InvalidPage
from django.db.models import Q
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse

# collector
from source.models import LinkSum, Collection, Source, Url


def home(request, template="webfront/home.html"):
    data = {
    }
    if request.user.is_authenticated():
        return redirect("webfront:collection")
    return render(request, template, data)

def login_view(request, template="webfront/login.html"):
    data = {}
    return render(request, template, data)

def search(request, template="webfront/search.html"):
    data = {}
    querystring = request.GET['query'].replace(' ', ' & ')

    links = LinkSum.objects.raw(
        """SELECT DISTINCT "source_linksum"."id", "source_linksum"."tags", "source_linksum"."summary", "source_linksum"."title", "source_linksum"."link", "source_linksum"."url_id", "source_linksum"."origin_id", "source_linksum"."source_id", "source_linksum"."read", "source_linksum"."recommanded", "source_linksum"."collection_id", "source_linksum"."inserted_at", "source_linksum"."user_id"
           FROM source_linksum
           INNER JOIN source_url ON
              (source_linksum.url_id = source_url.id)
           AND
              to_tsvector('english', source_url.content) @@ to_tsquery('english', %s)
           ORDER BY "source_linksum"."inserted_at" DESC;
         """, [querystring])

    data = {
        'links' : links,
        'collections' : Collection.objects.filter(Q(user__id=request.user.id)|Q(user__isnull=True)),
        'sources' : Source.objects.all(),
    }
    return render(request, template, data)


def get_display_paginate_item(paginator, page):
    max_page_display = 10
    page_range = []
    max_page = paginator.num_pages
    if page == 1:
        if max_page > max_page_display:
            page_range = range(1, max_page_display)
            page_range.append("...")
            page_range.append(max_page)

    elif page > 1 and page < max_page:
        firsts = range(1, page)[:5]
        lasts = range(page + 1, max_page)[:5]
        page_range = firsts + ["...", page, "..."] + lasts

    elif page == max_page:
        page_range = [1, "..."]
        page_range.append(range(max_page_display - 10, max_page_display))

    return page_range


@login_required
def links_today(request, collection=None, template="webfront/links_today.html"):
    show_read = True
    now = datetime.now()
    yesterday = datetime.now() - timedelta(days=1)
    if collection == "unread" or not collection:
        show_unread = False
        collection = "all"
    qs = LinkSum.objects.select_related('authors')\
                        .filter(hidden=False)\
                        .filter(user__id=request.user.id)\
                        .filter(inserted_at__range=(yesterday, now))\
                        .order_by('-recommanded')
    if not show_read:
        qs.filter(read=False)

    if collection:
        collection = Collection.objects.filter(Q(user__id=request.user.id)| Q(user__isnull=True))\
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
        'unread_count' : links.count(),
        'paginator' : paginator,
        'links' : links,
        'collections' : Collection.objects.filter(Q(user__id=request.user.id)|Q(user__isnull=True)),
        'sources' : Source.objects.all(),
        'page_range' : page_range,
    }

    return render(request, template, data)



@login_required
def collection(request, collection=None, template="webfront/collection.html"):
    show_read = True
    if collection == "unread" or not collection:
        show_unread = False
        collection = "all"
    collection = Collection.objects.filter(Q(user__id=request.user.id)| Q(user__isnull=True))\
                                   .get(name__iexact=collection)
    qs = LinkSum.objects.select_related('authors')\
                        .filter(user__id=request.user.id)\
                        .filter(hidden=False)\
                        .filter(collection__id=collection.id)\
                        .order_by('-pk')
    if not show_read:
        qs.filter(read=False)

    print request.user.id
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
        'unread_count' : links.count(),
        'paginator' : paginator,
        'links' : links,
        'collections' : Collection.objects.filter(Q(user__id=request.user.id)|Q(user__isnull=True)),
        'sources' : Source.objects.all(),
        'page_range' : page_range,
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
        'unread_count' : links.count(),
        'links' : links,
        'collections' : Collection.objects.filter(Q(user__id=request.user.id)|Q(user__isnull=True)),
        'sources' : Source.objects.all(),
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
        'unread_count' : links.count(),
        'links' : links,
        'sources' : Source.objects.all(),
        'collections' : Collection.objects.filter(Q(user__id=request.user.id)|Q(user__isnull=True)),
    }

    return render(request, template, data)

@login_required
def collection_user(request, user, source, template="webfront/collection.html"):
    show_read = True
    qs = LinkSum.objects.select_related('authors')\
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
        'unread_count' : links.count(),
        'paginator' : paginator,
        'links' : links,
        'collections' : Collection.objects.filter(Q(user__id=request.user.id)|Q(user__isnull=True)),
        'sources' : Source.objects.all(),
        'page_range' : page_range,
    }

    return render(request, template, data)

@login_required
def ajax_hide_linksum(request, linksum_id):
    if not request.is_ajax():
        return HttpResponse(status_code=400)

    link = get_object_or_404(LinkSum, pk=linksum_id, user_id=request.user.pk)
    link.hidden = True
    link.save()
