from django.conf.urls import url
from . import views


urlpatterns = [
    url(r'^$', views.index, name='index'),    
    url(r'^(?P<category_id>[0-9]+)/$', views.category, name = 'category'),
    url(r'^item/(?P<item_id>[0-9]+)/$', views.getItem, name = 'item'),
]