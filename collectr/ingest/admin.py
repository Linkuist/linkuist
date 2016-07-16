from django.contrib import admin

from . import models


class MediaAdmin(admin.ModelAdmin):
    pass

admin.site.register(models.Media, MediaAdmin)


class SharerAdmin(admin.ModelAdmin):
    pass

admin.site.register(models.Sharer, SharerAdmin)


class LinkAdmin(admin.ModelAdmin):
    pass

admin.site.register(models.Link, LinkAdmin)


class LinkMetadataAdmin(admin.ModelAdmin):
    pass

admin.site.register(models.LinkMetadata, LinkMetadataAdmin)
