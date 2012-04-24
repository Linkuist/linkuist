"""



"""
# django
from django.contrib import admin

# collectr
from collector.models import (CollectionItemType, CollectionItem, Collection,
                              Filter, Author, CollectionFilter)

class AuthorAdmin(admin.ModelAdmin):
    pass

class FilterAdmin(admin.ModelAdmin):
    list_display = ('user', 'filter', 'does_it_contain')

class CollectionItemTypeAdmin(admin.ModelAdmin):
    pass

class CollectionAdmin(admin.ModelAdmin):
    pass

class CollectionFilterAdmin(admin.ModelAdmin):
    list_display = ('user', 'collection', 'base_url')

class CollectionItemAdmin(admin.ModelAdmin):
    list_display = ('direct_link', 'type', 'summary', 'date', "is_read")


admin.site.register(Author, AuthorAdmin)
admin.site.register(Filter, FilterAdmin)
admin.site.register(Collection, CollectionAdmin)
admin.site.register(CollectionFilter, CollectionFilterAdmin)
admin.site.register(CollectionItem, CollectionItemAdmin)
admin.site.register(CollectionItemType, CollectionItemTypeAdmin)
