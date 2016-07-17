from django.conf import settings
from django.conf.urls import include, url
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = [
    # Examples:
    # url(r'^$', 'collectr.views.home', name='home'),
    # url(r'^collectr/', include('collectr.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),
    url(r'', include('social.apps.django_app.urls', namespace='social')),
    url(r'', include('collectr.webfront.urls', namespace='webfront')),
    url(r'', include('collectr.link_tracking.urls', namespace='link_tracking')),
    url(r'^collector/', include('collectr.collector.urls', namespace='collector')),
    url(r'^profile/', include('collectr.userprofile.urls', namespace='userprofile')),
    url(r'^api/', include('collectr.webapi.urls')),
]

if settings.DEBUG:
    urlpatterns += staticfiles_urlpatterns()
