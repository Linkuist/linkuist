# django
from django.conf.urls.defaults import patterns, include, url
from django.contrib.auth.views import login, logout

# localapp
from link_tracking import views

urlpatterns = patterns('',
    url(r'^l/(?P<link_id>\d+)/$', views.track_link, name="track_link"),
)

