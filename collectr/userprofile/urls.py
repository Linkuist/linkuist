# django
from django.conf.urls.defaults import patterns, url

# localapp
from userprofile import views

urlpatterns = patterns('',
    url(r'^$', views.home, name="home"),
    url(r'^rss/$', views.rss, name="rss"),
    url(r'^rss/add/$', views.add_rss, name="add_rss"),
    url(r'^filters/$', views.filters, name="filters"),
)
