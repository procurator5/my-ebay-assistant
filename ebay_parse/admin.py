from django.contrib import admin

from .models import Setting
from .models import eBayCategory
#from Onboard.KeyCommon import actions
from mptt.admin import MPTTModelAdmin
from mptt.admin import DraggableMPTTAdmin
from django.conf.urls import url
from django.http import HttpResponseRedirect, HttpResponse
from django.core.urlresolvers import reverse

import urllib.request
import json
from django.contrib.admin.templatetags.admin_list import admin_list_filter
from django.http import HttpResponseRedirect
from ebay_parse.views import category

class SettingAdmin(admin.ModelAdmin):
    list_display=('setting_name', 'setting_value')
    
class eBayCategoryAdmin(DraggableMPTTAdmin):
    list_editable = ['ebay_category_enabled']
    actions = [ 'enableCategoyWithParents' ]
    search_fields = [ 'ebay_category_name' ]

    change_list_template = 'admin/ebay_parse/ebaycategory/change_list.html'
    #: resource class
    resource_class = None
    #: import data encoding
    from_encoding = "utf-8"
    skip_admin_log = None
    # storage class for saving temporary files
    tmp_storage_class = None

    def get_model_info(self):
        # module_name is renamed to model_name in Django 1.8
        app_label = self.model._meta.app_label
        try:
            return (app_label, self.model._meta.model_name,)
        except AttributeError:
            return (app_label, self.model._meta.module_name,)    

    def get_urls(self):
        urls = super(eBayCategoryAdmin, self).get_urls()
        info = self.get_model_info()
        my_urls = [
            url(r'^load/$',
                self.admin_site.admin_view(self.loadCategories),
                name='%s_%s_load' % info),
        ]
        return my_urls + urls

    
    def loadCategories(self, request, *args, **kwargs):
        print(Setting.getIntValue('ParentCategory'))
        self.stepLoadCategory(Setting.getIntValue('ParentCategory'))
        self.message_user(request, 'Loaded success...')  
        url = reverse('admin:%s_%s_changelist' % self.get_model_info(),
                          current_app=self.admin_site.name)
        return HttpResponseRedirect(url)    
    
            
    def stepLoadCategory(self, category_id):
        response = GetCategoryInfo(category_id, include_selector='ChildCategories' )
        api_resp = json.loads(response.decode('utf-8'))
        categories = api_resp['CategoryArray']['Category']
        for category in categories:
            item = eBayCategory(ebay_category_id = int(category['CategoryID']),
                                ebay_category_name = category['CategoryName'],
                                )
            if int(category['CategoryParentID']) != 0:
                try:
                    item.parent = eBayCategory.objects.get(ebay_category_id = int(category['CategoryParentID']))
                except eBayCategory.DoesNotExist:
                    pass
            
            item.save()
            if int(category['CategoryID']) != category_id: 
                self.stepLoadCategory(int(category['CategoryID']))
                
    def enableCategoyWithParents(self, request, queryset):
        for category in queryset:
            self.enableCategoryrecursive(category)
            
    def enableCategoryrecursive(self, category):
        category.ebay_category_enabled=True
        category.save()
        for sub in category.get_children():
            self.enableCategoryrecursive(sub)
        
    
    loadCategories.short_description = 'Load Categories from eBay.com'

# Register your models here.
admin.site.register(Setting, SettingAdmin)
admin.site.register(eBayCategory, eBayCategoryAdmin,
    list_display=(
        'tree_actions',
        'ebay_category_name',
        'ebay_category_enabled',
        # ...more fields if you feel like it...
    ),
    list_display_links=(
        'ebay_category_name',
    ),
    )

# Utilities
def GetCategoryInfo(category_id, include_selector=None, encoding="JSON"):
    if category_id:
        user_param = {
            'callname': GetCategoryInfo.__name__,
            'responseencoding': encoding,
            'CategoryID': category_id}

    if include_selector:
        user_param['IncludeSelector'] = include_selector

    response = get_response(user_param)
    return response

#requests method
def get_response(user_params):
    app_id = Setting.objects.filter(setting_name='AppID').values('setting_value')[0]['setting_value']
    site_id = 'EBAY-US'
    version = 967
    endpoint = 'http://open.api.ebay.com/shopping?'

    d = dict(appid=app_id, siteid=site_id, version=version)

    d.update(user_params)

    try:
        req = urllib.request.Request(endpoint + urllib.parse.urlencode(d), method='GET')
        res = urllib.request.urlopen(req)
    except Exception as e:
        return str(e)
    data = res.read()
    return data


