# django
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render

from userprofile import forms

@login_required
def home(request):

    return render(request, 'userprofile/home.html')


@login_required
def rss(request):

    form = forms.RssForm(request.user, data=request.POST or None)
    if request.method == 'POST' and form.is_valid():
        to_add = form.cleaned_data['feeds']
        to_del = list(set(form.fields['feeds'].initial) - set(to_add))

        for feed in to_add:
            feed.users.add(request.user)

        for feed in to_del:
            feed.users.remove(request.user)
        return redirect('userprofile:home')

    data = {
        'form': form,
    }
    return render(request, 'userprofile/rss.html', data)


@login_required
def filters(request):

    form = forms.FiltersForm(request.user, data=request.POST or None)
    if request.method == 'POST' and form.is_valid():
        for filtr in forms.filters:
            pass
        return redirect('userprofile:home')

    data = {
        'form': form,
    }
    return render(request, 'userprofile/filters.html', data)
