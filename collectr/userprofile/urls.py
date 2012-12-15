# django
from django.conf.urls.defaults import patterns, include, url
from django.contrib.auth.views import login, logout

# localapp
from userprofile import views

urlpatterns = patterns('',
    url(r'^$', views.home, name="home"),
    url(r'^rss/$', views.rss, name="rss"),
    url(r'^filters/$', views.filters, name='filters'),
)

