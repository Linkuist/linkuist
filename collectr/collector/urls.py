# django
from django.conf.urls.defaults import patterns, include, url

# localapp
from collector import views

urlpatterns = patterns('',
    url(r'^bookmark/(?P<username>\w+)/$', views.SubmitBookmarkView.as_view(), name="bookmark"),
)

