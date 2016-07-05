# django
from django.conf.urls.defaults import patterns, include, url
from django.contrib.auth.views import login, logout

# localapp
from collectr.webfront import views

urlpatterns = patterns('',
    url(r'^$', views.home, name="home"),
    url(r'^search/$', views.SearchView.as_view(), name="search"),
    url(r'^login/$', login, {'template_name': 'webfront/login.html'}, name="login"),
    url(r'^logout/$', login, name="logout"),
    url(r'^links/(?P<period>today|yesterday|(this|last)_(week|month))/$', views.DateView.as_view(), name="links_today"),
    url(r'^collection/$', views.CollectionView.as_view(), name="collection"),
    url(r'^collection/(?P<collection>\w+)/$', views.CollectionView.as_view(), name="collection"),
    url(r'^collection/source/(?P<source>\w+)/$', views.SourceView.as_view(), name="collection_source"),
    url(r'^collection/tag/(?P<tag>.*)/$', views.CollectionTagView.as_view(), name="collection_tag"),
    url(r'^collection/user/(?P<user>.*)/(?P<source>\w+)/$', views.CollectionUserView.as_view(), name="collection_user"),
)
