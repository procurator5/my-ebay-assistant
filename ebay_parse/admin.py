from django.contrib import admin

from .models import Setting
from .models import eBayCategory
from xdiagnose.info import SHORT_DESCRIPTION
from Onboard.KeyCommon import actions

class SettingAdmin(admin.ModelAdmin):
    list_display=('setting_name', 'setting_value')
    
class eBayCategoryAdmin(admin.ModelAdmin):
    list_display=('ebay_category_id', 'ebay_category_name', 'ebay_category_parent','ebay_category_enabled')
    search_fields = ['ebay_category_name']
    list_editable = ['ebay_category_enabled']
    
    actions = ['loadCategories']
    
    def loadCategories(self, request, queryset):
        pass
    
    loadCategories.short_description = 'Load Categories from eBay.com'

# Register your models here.
admin.site.register(Setting, SettingAdmin)
admin.site.register(eBayCategory, eBayCategoryAdmin)