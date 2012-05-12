# Create your views here.

# django
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect

# collector
from source.models import LinkSum, Collection


def home(request, template="webfront/home.html"):
    data = {
    }
    if request.user.is_authenticated():
        return redirect("webfront:collection")
    return render(request, template, data)

def login_view(request, template="webfront/login.html"):
    data = {}
    return render(request, template, data)

@login_required
def collection(request, collection=None, template="webfront/collection.html"):
    show_read = True
    if collection == "unread" or not collection:
        show_unread = False
        collection = "all"
    collection = Collection.objects.get(name__iexact=collection, user__id=request.user.id)
    links = LinkSum.objects.filter(user__id=request.user.id)\
                           .filter(collection__id=collection.id)\
                           .order_by('-pk')[:100]
    if not show_read:
        links.filter(read=False)

    data = {
        'unread_count' : links.count(),
        'links' : links,
        'collections' : Collection.objects.filter(user__id=request.user.id)
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
        'collections' : Collection.objects.filter(user__id=request.user.id)
    }

    return render(request, template, data)
