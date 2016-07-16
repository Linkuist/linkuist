from django.conf.urls import url

from . import views


urlpatterns = [
    url(r'^$', views.LinkView.as_view(), name="links"),
]
