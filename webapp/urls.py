from django.conf.urls import include, url
from .views import sw_import,index

urlpatterns = [
    url(r'^sw-import.js', sw_import),
    url(r'^', index)
]
