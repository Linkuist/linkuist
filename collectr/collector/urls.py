# django
from django.conf.urls import url

# localapp
from . import views

urlpatterns = [
    url(r'^bookmark/(?P<username>\w+)/$', views.SubmitBookmarkView.as_view(), name="bookmark"),
]

