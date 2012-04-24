from django.conf.urls.defaults import patterns, include, url

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
from django.contrib import sites
admin.autodiscover()
admin.site.unregister(sites.models.Site)

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'collectr.views.home', name='home'),
    # url(r'^collectr/', include('collectr.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),
    url(r'^collection/', include('collector.urls', namespace='collector')),
    url(r'', include('social_auth.urls')),

)
