from django.conf.urls import url
from . import views


urlpatterns = [
    url(r'^$', views.index, name='index'),    
    url(r'^category/(?P<category_id>[0-9]+)/$', views.category, name = 'category'),
    url(r'^(?P<species_id>[0-9]+)/$', views.species, name = 'species'),
    url(r'^genus/(?P<genus_id>[\w+]+)/$', views.genus, name = 'genus'),
    url(r'^delete/(?P<item_id>[\w+]+)/$', views.item_delete, name = 'item_delete'),
    url(r'^search/$', views.search, name = 'search'),
    url(r'^best/$', views.best, name = 'best'),
]