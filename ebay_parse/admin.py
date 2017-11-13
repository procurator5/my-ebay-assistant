from django.contrib import admin

from .models import Setting
from .models import eBayCategory
from Onboard.KeyCommon import actions
from mptt.admin import MPTTModelAdmin
from mptt.admin import DraggableMPTTAdmin

import urllib.request
import json

class SettingAdmin(admin.ModelAdmin):
    list_display=('setting_name', 'setting_value')
    
class eBayCategoryAdmin(DraggableMPTTAdmin):
    list_editable = ['ebay_category_enabled']
    actions = ['loadCategories']
    
    def loadCategories(self, request, queryset):
        self.stepLoadCategory(-1)
        self.message_user(request, 'Loaded success...')
        
    def stepLoadCategory(self, category_id):
        response = GetCategoryInfo(category_id, include_selector='ChildCategories' )
        api_resp = json.loads(response.decode('utf-8'))
        categories = api_resp['CategoryArray']['Category']
        for category in categories:
            item = eBayCategory(ebay_category_id = int(category['CategoryID']),
                                ebay_category_name = category['CategoryName'],
                                )
            if int(category['CategoryParentID']) != 0:
                item.parent = eBayCategory.objects.get(ebay_category_id = int(category['CategoryParentID']))
            item.save()
            if int(category['CategoryID']) != category_id: 
                print(category['CategoryID'])
                self.stepLoadCategory(int(category['CategoryID']))
        
    
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


