# django
from django.conf.urls.defaults import patterns, include, url

# localapp
from collector import views

# celery
from djcelery import views as celery_views


urlpatterns = patterns('',
    url(r'^$', views.home, name="home"),
    url(r'^task/(?P<task_name>.+?)/', celery_views.apply),
)

