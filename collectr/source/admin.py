# -*- coding: latin-1 -*-
"""

"""

# admin
from django.contrib import admin
from django.contrib import sites
# local
from source import models


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
    pass

class SourceAdmin(admin.ModelAdmin):
    pass

class RssAdmin(admin.ModelAdmin):
    pass

admin.site.register(models.Filter, FilterAdmin)
admin.site.register(models.LinkSum, LinkSumAdmin)
admin.site.register(models.Source, SourceAdmin)
admin.site.register(models.Collection, CollectionAdmin)
admin.site.register(models.Url, UrlAdmin)
admin.site.register(models.Tag, TagAdmin)
admin.site.register(models.UrlViews, UrlViewsAdmin)
admin.site.register(models.Rss, RssAdmin)

admin.site.unregister(sites.models.Site)
