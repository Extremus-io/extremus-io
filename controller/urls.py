from django.conf.urls import include, url
from . import views


urlpatterns = [
    url(r'^(?P<pk>[0-9]).json', views.ControllerView),
    url(r'^.json$', views.ControllerList),
]
