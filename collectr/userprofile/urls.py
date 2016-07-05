# django
from django.conf.urls.defaults import patterns, url

# localapp
from . import views

urlpatterns = patterns('',
    url(r'^$', views.home, name="home"),
    url(r'^rss/$', views.SelectRSSView.as_view(), name="rss"),
    url(r'^rss/add/$', views.AddRSSView.as_view(), name="add_rss"),
    url(r'^filters/$', views.filters, name="filters"),
)
