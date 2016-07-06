# django
from django.conf.urls import url

# localapp
from . import views

urlpatterns = [
    url(r'^l/(?P<link_id>\d+)/$', views.track_link, name="track_link"),
]
