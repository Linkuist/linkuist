# -*- coding: latin-1 -*-
"""

"""

# admin
from django.contrib import admin

# local
from source.models import Source, LinkSum

class LinkSumAdmin(admin.ModelAdmin):
    list_display = ('pk', 'author', 'tags', 'link_title', 'reco', 'summary')


    def queryset(self, request):
        qs = super(LinkSumAdmin, self).queryset(request)
        return qs.filter(user__id=request.user.id)

class SourceAdmin(admin.ModelAdmin):
    pass

admin.site.register(LinkSum, LinkSumAdmin)
admin.site.register(Source, SourceAdmin)
