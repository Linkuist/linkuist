# -*- coding: latin-1 -*-
"""

"""

# admin
from django.contrib import admin
from django.contrib import sites
# local
from source.models import (Source, LinkSum, Collection,
                           Filter, Tag, Url, UrlViews,
                           Rss)

class TagAdmin(admin.ModelAdmin):
    pass

class UrlAdmin(admin.ModelAdmin):
    pass

class UrlViewsAdmin(admin.ModelAdmin):
    pass

class FilterAdmin(admin.ModelAdmin):
    pass

class CollectionAdmin(admin.ModelAdmin):
    pass

class LinkSumAdmin(admin.ModelAdmin):
    list_display = ('pk', 'tags', 'link_title', 'reco', 'summary')

class SourceAdmin(admin.ModelAdmin):
    pass

class RssAdmin(admin.ModelAdmin):
    pass

admin.site.register(Filter, FilterAdmin)
admin.site.register(LinkSum, LinkSumAdmin)
admin.site.register(Source, SourceAdmin)
admin.site.register(Collection, CollectionAdmin)
admin.site.register(Url, UrlAdmin)
admin.site.register(Tag, TagAdmin)
admin.site.register(UrlViews, UrlViewsAdmin)
admin.site.register(Rss, RssAdmin)

admin.site.unregister(sites.models.Site)
