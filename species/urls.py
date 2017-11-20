from django.conf.urls import url
from . import views


urlpatterns = [
    url(r'^$', views.index, name='index'),    
    url(r'^category/(?P<category_id>[0-9]+)/$', views.category, name = 'category'),
    url(r'^(?P<species_id>[0-9]+)/$', views.species, name = 'species'),
]