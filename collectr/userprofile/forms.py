# python
from itertools import chain

# django
from django import forms
from django.utils.encoding import force_unicode
from django.utils.html import conditional_escape
from django.utils.safestring import mark_safe

# source

from source import models as source_models


class TableCheckboxSelectMultiple(forms.SelectMultiple):

    def render(self, name, value, attrs=None, choices=()):
        if value is None: value = []
        has_id = attrs and 'id' in attrs
        final_attrs = self.build_attrs(attrs, name=name)
        output = [u'']
        # Normalize to strings
        str_values = set([force_unicode(v) for v in value])
        for i, (option_value, option_label) in enumerate(chain(self.choices, choices)):
            # If an ID attribute was given, add a numeric index as a suffix,
            # so that the checkboxes don't all have the same ID attribute.
            if has_id:
                final_attrs = dict(final_attrs, id='%s_%s' % (attrs['id'], i))
                label_for = u' for="%s"' % final_attrs['id']
            else:
                label_for = ''

            cb = forms.CheckboxInput(final_attrs, check_test=lambda value: value in str_values)
            option_value = force_unicode(option_value)
            rendered_cb = cb.render(name, option_value)
            option_label = conditional_escape(force_unicode(option_label))
            output.append(u'<tr><td><label%s>%s</label></td><td>%s</td></tr>' % (label_for, option_label, rendered_cb))
        output.append(u'')
        return mark_safe(u'\n'.join(output))

    def id_for_label(self, id_):
        # See the comment for RadioSelect.id_for_label()
        if id_:
            id_ += '_0'
        return id_


class FiltersForm(forms.Form):
    filters = forms.ModelMultipleChoiceField(queryset=source_models.Filter.objects.all(),
        widget=TableCheckboxSelectMultiple)

    def __init__(self, user, *args, **kwargs):
        super(FiltersForm, self).__init__(*args, **kwargs)
        self.fields['filters'].queryset = self.fields['filters'].queryset.filter(user=user)


class RssForm(forms.Form):
    feeds = forms.ModelMultipleChoiceField(queryset=source_models.Rss.objects.all(),
        widget=TableCheckboxSelectMultiple)

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super(RssForm, self).__init__(*args, **kwargs)
        self.fields['feeds'].initial = source_models.Rss.objects.filter(users=user)


class AddRssForm(forms.ModelForm):

    class Meta:
        model = source_models.Rss
        fields = ['link', 'name']
    

