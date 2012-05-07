# -*- coding: latin-1 -*-
"""

"""

# admin
from django.contrib import admin

# local
from source.models import Source, LinkSum, Collection, Filter

class FilterAdmin(admin.ModelAdmin):
    pass

class CollectionAdmin(admin.ModelAdmin):
    pass

class LinkSumAdmin(admin.ModelAdmin):
    list_display = ('pk', 'author', 'tags', 'link_title', 'reco', 'summary')


    def queryset(self, request):
        qs = super(LinkSumAdmin, self).queryset(request)
        return qs.filter(user__id=request.user.id)

class SourceAdmin(admin.ModelAdmin):
    pass

admin.site.register(Filter, FilterAdmin)
admin.site.register(LinkSum, LinkSumAdmin)
admin.site.register(Source, SourceAdmin)
admin.site.register(Collection, CollectionAdmin)
