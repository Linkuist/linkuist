# Create your views here.

# django
from django.contrib.auth.decorators import login_required
from django.shortcuts import render

# collector
from source.models import LinkSum
from collector.models import Collection


def home(request, template="webfront/home.html"):
    data = {}
    return render(request, template, data)

def login_view(request, template="webfront/login.html"):
    data = {}
    return render(request, template, data)

@login_required
def collection(request, template="webfront/collection.html"):
    links = LinkSum.objects.filter(user__id=request.user.id).order_by('-pk')[:100]
    data = {
        'links' : links,
        'collections' : Collection.objects.filter(user__id=request.user.id)
    }

    return render(request, template, data)
