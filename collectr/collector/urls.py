from django.conf.urls.defaults import patterns, include, url

from collector import views

urlpatterns = patterns('',
    url(r'^$', views.home, name="home"),
)

