# Create your views here.

# django
from django.contrib.auth.decorators import login_required
from django.shortcuts import render

# collector
from source.models import LinkSum, Collection


def home(request, template="webfront/home.html"):
    data = {}
    return render(request, template, data)

def login_view(request, template="webfront/login.html"):
    data = {}
    return render(request, template, data)

@login_required
def collection(request, collection=None, template="webfront/collection.html"):
    if not collection:
        collection = "all"
    collection = Collection.objects.get(name__iexact=collection, user__id=request.user.id)
    links = LinkSum.objects.filter(user__id=request.user.id)\
                           .filter(collection__id=collection.id)\
                           .order_by('-pk')[:100]
    data = {
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
        'links' : links,
        'collections' : Collection.objects.filter(user__id=request.user.id)
    }

    return render(request, template, data)
