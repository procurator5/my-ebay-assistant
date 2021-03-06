from django.conf.urls import url
from . import views


urlpatterns = [
    url(r'^$', views.index, name='index'),    
    url(r'^(?P<category_id>[0-9]+)/$', views.category, name = 'category'),
    url(r'^load/(?P<category_id>[0-9]+)/$', views.loadCategory, name = 'load'),
    url(r'^item/(?P<item_id>[0-9]+)/$', views.getItem, name = 'item'),
    url(r'^item/delete/(?P<item_id>[0-9]+)/$', views.deleteItem, name = 'delete'),
    url(r'^save/$', views.saveSpecies, name = 'save'),
]