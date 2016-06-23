# django
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.shortcuts import redirect, render
from django.utils.decorators import method_decorator
from django.views.generic.edit import CreateView, FormView

from userprofile import forms


class LoginRequiredMixin(object):
    """User must be logged in to access this view."""

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(LoginRequiredMixin, self).dispatch(*args, **kwargs)


@login_required
def home(request):
    return render(request, 'userprofile/home.html')


class SelectRSSView(LoginRequiredMixin, FormView):

    form_class = forms.RssForm
    template_name = 'userprofile/rss.html'

    def get_success_url(self):
        return reverse('userprofile:rss')

    def get_form_kwargs(self):
        kwargs = super(SelectRSSView, self).get_form_kwargs()
        kwargs.update({'user': self.request.user})
        return kwargs

    def form_valid(self, form):
        to_add = form.cleaned_data['feeds']
        to_del = list(set(form.fields['feeds'].initial) - set(to_add))

        for feed in to_add:
            feed.users.add(self.request.user)

        for feed in to_del:
            feed.users.remove(self.request.user)

        super(SelectRSSView, self).form_valid(self, form)


class AddRSSView(LoginRequiredMixin, CreateView):

    form_class = forms.AddRssForm
    template_name = 'userprofile/add_rss.html'

    def get_success_url(self):
        return reverse('userprofile:rss')


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
