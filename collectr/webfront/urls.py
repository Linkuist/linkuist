# django
from django.conf.urls.defaults import patterns, include, url
from django.contrib.auth.views import login, logout

# localapp
from webfront import views

urlpatterns = patterns('',
    url(r'^$', views.home, name="home"),
    url(r'^search/$', views.search, name="search"),
    url(r'^login/$', login, {'template_name': 'webfront/login.html'}, name="login"),
    url(r'^logout/$', login, name="logout"),
    url(r'^links/today/$', views.links_today, name="links_today"),
    url(r'^collection/$', views.collection, name="collection"),
    url(r'^collection/(?P<collection>\w+)/$', views.collection, name="collection"),
    url(r'^collection/source/(?P<source>\w+)/$', views.collection_source, name="collection_source"),
    url(r'^collection/tag/(?P<tag>.*)/$', views.collection_tag, name="collection_tag"),
    url(r'^collection/user/(?P<user>.*)/(?P<source>\w+)/$', views.collection_user, name="collection_user"),
)

