# -*- coding: latin-1 -*-
"""

"""

# admin
from django.contrib import admin
from django.contrib import sites
# local
from source import models

class CollectionAdmin(admin.ModelAdmin):
    list_display = ('user', 'name')


class FilterAdmin(admin.ModelAdmin):
    list_display = ('user', 'regexp', 'field', 'to_delete', 'to_collection')


class SourceAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')


class UrlViewsAdmin(admin.ModelAdmin):
    list_display = ('count',)


class TagAdmin(admin.ModelAdmin):
    list_display = ('name',)


class UrlAdmin(admin.ModelAdmin):
    list_display = ('link', 'title', 'inserted_at')


class AuthorAdmin(admin.ModelAdmin):
    list_display = ('name', 'source')


class LinkSumAdmin(admin.ModelAdmin):
    list_display = ('user', 'inserted_at', 'url', 'read', 'recommanded', 'hidden')
    list_filter = ('user',)


class RssAdmin(admin.ModelAdmin):
    list_display = ('name', 'link', 'etag')


class RedditAdmin(admin.ModelAdmin):
    list_display = ('subreddit', 'uid')


admin.site.register(models.Filter, FilterAdmin)
admin.site.register(models.LinkSum, LinkSumAdmin)
admin.site.register(models.Source, SourceAdmin)
admin.site.register(models.Collection, CollectionAdmin)
admin.site.register(models.Url, UrlAdmin)
admin.site.register(models.Tag, TagAdmin)
admin.site.register(models.UrlViews, UrlViewsAdmin)
admin.site.register(models.Rss, RssAdmin)
admin.site.register(models.Reddit, RedditAdmin)
admin.site.unregister(sites.models.Site)
