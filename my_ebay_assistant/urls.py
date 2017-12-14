"""my_ebay_assistant URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import include, url
from django.contrib import admin
from django.conf.urls.static import static
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.conf import settings
from django.contrib.auth.views import login
from django.template import loader
from django.http import HttpResponse
from ebay_parse.models import eBayCategory

def index(request):
    template = loader.get_template("index.html")
    context = {
                'nodes': eBayCategory.objects.all(),
                }
    return HttpResponse(template.render(context, request))

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^admin_tools/', include('admin_tools.urls')),
    url(r'^ebay_parse/', include('ebay_parse.urls')),
    url(r'^species/', include('species.urls')),
    url(r'^img/', include('gallery.urls')),
    url('^', include('django.contrib.auth.urls')),
    url('^login/$', login, name='login'),
    url(r'^$', index, name='index'),    
]

# В конце файла:

if settings.DEBUG:

    if settings.MEDIA_ROOT:

        urlpatterns += static(settings.MEDIA_URL,

            document_root=settings.MEDIA_ROOT)

# Эта строка опциональна и будет добавлять url'ы только при DEBUG = True

urlpatterns += staticfiles_urlpatterns()
