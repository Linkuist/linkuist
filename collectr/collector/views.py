# django
from django.contrib.auth.decorators import login_required
from django.shortcuts import render

#collector
from collector.models import Collection, CollectionItem

@login_required
def home(request, template_name="collection/home.html"):

    collections = Collection.objects.all()

    data = {
        'collections' : collections,
    }

    return render(request, template_name, data)
