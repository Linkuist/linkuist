# Create your views here.

# django
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import render, redirect

# collector
from source.models import LinkSum, Collection, Source


def home(request, template="webfront/home.html"):
    data = {
    }
    if request.user.is_authenticated():
        return redirect("webfront:collection")
    return render(request, template, data)

def login_view(request, template="webfront/login.html"):
    data = {}
    return render(request, template, data)


def get_display_paginate_item(paginator, page):
    max_page_display = 10
    page_range = []
    max_page = paginator.num_pages
    print "page:", page
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

    print page_range
    return page_range

@login_required
def collection(request, collection=None, template="webfront/collection.html"):
    show_read = True
    if collection == "unread" or not collection:
        show_unread = False
        collection = "all"
    collection = Collection.objects.get(name__iexact=collection, user__id=request.user.id)
    qs = LinkSum.objects.filter(user__id=request.user.id)\
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
        'unread_count' : links.count(),
        'paginator' : paginator,
        'links' : links,
        'collections' : Collection.objects.filter(user__id=request.user.id),
        'sources' : Source.objects.all(),
        'page_range' : page_range,
    }

    return render(request, template, data)

@login_required
def collection_source(request, source, template="webfront/collection.html"):
    links = LinkSum.objects.filter(user__id=request.user.id)\
                           .filter(source__slug=source)\
                           .order_by('-pk')[:100]
    data = {
        'unread_count' : links.count(),
        'links' : links,
        'collections' : Collection.objects.filter(user__id=request.user.id),
        'sources' : Source.objects.all(),
    }

    return render(request, template, data)


@login_required
def collection_tag(request, tag, template="webfront/collection.html"):
    links = LinkSum.objects.filter(user__id=request.user.id)\
                           .filter(url__tags__name=tag)\
                           .order_by('-pk')[:100]
    data = {
        'unread_count' : links.count(),
        'links' : links,
        'sources' : Source.objects.all(),
        'collections' : Collection.objects.filter(user__id=request.user.id)
    }

    return render(request, template, data)
