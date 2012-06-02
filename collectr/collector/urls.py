# django
from django.conf.urls.defaults import patterns, include, url

# localapp
from collector import views

# celery
#from djcelery import views as celery_views


urlpatterns = patterns('',
    url(r'^bookmark/$', views.bookmark, name="bookmark"),
    url(r'^bookmark/secret/(?P<username>\w+)/$', views.secret_bookmark, name="secret_bookmark"),
#    url(r'^task/(?P<task_name>.+?)/', celery_views.apply),
)

