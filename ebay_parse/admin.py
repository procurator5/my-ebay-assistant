from django.contrib import admin

from .models import Setting
from .models import eBayCategory
from Onboard.KeyCommon import actions
from mptt.admin import MPTTModelAdmin
from mptt.admin import DraggableMPTTAdmin

class SettingAdmin(admin.ModelAdmin):
    list_display=('setting_name', 'setting_value')
    
class eBayCategoryAdmin(DraggableMPTTAdmin):
    list_editable = ['ebay_category_enabled']
    actions = ['loadCategories']
    
    def loadCategories(self, request, queryset):
        pass
    
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
    ),)