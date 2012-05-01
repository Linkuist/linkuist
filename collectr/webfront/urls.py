# django
from django.conf.urls.defaults import patterns, include, url
from django.contrib.auth.views import login, logout
# localapp
from webfront import views

urlpatterns = patterns('',
    url(r'^$', views.home, name="home"),
    url(r'^login/$', login, {'template_name': 'webfront/login.html'}, name="login"),
    url(r'^collection/$', views.collection, name="collection"),
)

