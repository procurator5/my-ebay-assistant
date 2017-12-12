from django.core.files.images import ImageFile
from django.db import models
import os
import urllib
from mptt.models import MPTTModel, TreeForeignKey
from species.models import Scpecies2Item

# Create your models here.
def load_empty_image():
    return "icons/blank.png"

class Setting(models.Model):
    setting_name = models.CharField(max_length=128)
    setting_value = models.CharField(max_length=128)
    setting_comment = models.CharField(max_length=256)
    setting_comment.null = True
    
    def getIntValue(name):
        try:
            return int( Setting.objects.filter(setting_name=name).values('setting_value')[0]['setting_value'])
        except IndexError:
            return 0

    def getValue(name):
        try:
            return Setting.objects.filter(setting_name=name).values('setting_value')[0]['setting_value']
        except IndexError:
            return ''
    
    getValue = staticmethod(getValue)
    getIntValue = staticmethod(getIntValue)

#Модель для хранения отдельных лотов eBay
class eBayItem(models.Model):
    ebay_item_id = models.BigIntegerField()
    ebay_item_id.primary_key = True
    ebay_item_id.Unique = True
    ebay_item_title = models.CharField(max_length=256)
    ebay_category = models.ForeignKey('eBayCategory', on_delete=models.CASCADE)
    ebay_item_url = models.URLField()
    payment_method = models.ForeignKey('eBayPaymentMethod', on_delete = models.SET_NULL, null=True, blank=True)
    ebay_item_postalcode = models.CharField(max_length=10)
    ebay_item_location = models.CharField(max_length=256)
    country = models.ForeignKey('Country', on_delete = models.SET_NULL, null=True, blank=True)
    ebay_item_price = models.DecimalField(max_digits = 10, decimal_places=2)
    ebay_item_shipping_price = models.DecimalField(max_digits = 5, decimal_places=2)
    ebay_item_starttime = models.DateTimeField()
    ebay_item_endtime = models.DateTimeField()
    listing_type = models.ForeignKey('ListingType', on_delete = models.SET_NULL, null=True, blank=True)
    ebay_watch_count = models.IntegerField()
    ebay_gallery_icon = models.ImageField(default=load_empty_image, upload_to='icons')
    ebay_item_description = models.TextField(null=True, blank=True)
    
    def relationIsExists(self):
        return Scpecies2Item.objects.filter(item = self).exists()

    def loadIcon(self, url):
        try:
            myItem = eBayItem.objects.get(pk = self.ebay_item_id)
            if myItem.ebay_gallery_icon == 'icons/blank.png':
                result = urllib.request.urlretrieve(url)
                self.ebay_gallery_icon.save(
				os.path.basename(url),
				ImageFile(open(result[0], 'rb'))
			    )
                os.remove(result[0])
            else:
                self.ebay_gallery_icon = myItem.ebay_gallery_icon
        except eBayItem.DoesNotExist:
            result = urllib.request.urlretrieve(url)
            self.ebay_gallery_icon.save(
			os.path.basename(url),
			ImageFile(open(result[0], 'rb'))
		    )
            os.remove(result[0])
            
    def getItemsForSpecies(species_id):
        return eBayItem.objects.raw("""
        SELECT ebi.* 
            FROM ebay_parse_ebayitem ebi
            JOIN species_scpecies2item si ON si.item_id = ebi.ebay_item_id
            WHERE si.species_id =%s; 
        """, params = [species_id])
        
    def getUndefinedItems(category_id = None, limit = 0, offset = 0):
        if limit == 0:
            return eBayItem.objects.raw("""
            SELECT ebay_item_id, ebay_item_title, ebay_item_url, ebay_item_postalcode, 
                   ebay_item_location, ebay_item_price, ebay_item_shipping_price, 
                   ebay_item_starttime, ebay_item_endtime, ebay_watch_count, country_id, 
                   ebay_category_id, listing_type_id, payment_method_id, ebay_gallery_icon, 
                   ebay_item_description
              FROM ebay_parse_ebayitem ei
              LEFT JOIN species_scpecies2item si ON ei.ebay_item_id = si.item_id
              WHERE si.id IS NULL;
            """)
        return eBayItem.objects.raw("""
        SELECT ebay_item_id, ebay_item_title, ebay_item_url, ebay_item_postalcode, 
               ebay_item_location, ebay_item_price, ebay_item_shipping_price, 
               ebay_item_starttime, ebay_item_endtime, ebay_watch_count, country_id, 
               ebay_category_id, listing_type_id, payment_method_id, ebay_gallery_icon, 
               ebay_item_description
          FROM ebay_parse_ebayitem ei
          LEFT JOIN species_scpecies2item si ON ei.ebay_item_id = si.item_id
          WHERE si.id IS NULL AND ebay_category_id = %s
          LIMIT %s OFFSET %s;
        """, [int(category_id), limit, offset])

    getItemsForSpecies = staticmethod(getItemsForSpecies)
    getUndefinedItems = staticmethod(getUndefinedItems)
                

class eBayCategory(MPTTModel):
    ebay_category_id = models.AutoField()
    ebay_category_id.primary_key = True
    ebay_category_name = models.CharField(max_length=256)
    parent = TreeForeignKey('self', null = True, blank = None, related_name = 'children' )
    ebay_category_enabled = models.BooleanField(default = False)
    
    def space(self):
        return '--' * self.get_level() + '>'
    
    def __unicode__(self):
        return self.ebay_category_name

class eBayPaymentMethod(models.Model):
    payment_method_id = models.AutoField()
    payment_method_id.primary_key = True
    payment_method_name = models.CharField(max_length=64)

class Country(models.Model):
    country_id = models.AutoField(primary_key = True)
    country_name = models.CharField(max_length = 64)

class ListingType(models.Model):
    listing_type_id = models.AutoField(primary_key = True)
    listing_type_name = models.CharField(max_length = 64)

#Модель для хранения фоток лота
class eBayItemGallery(models.Model):
    ebay_item = models.ForeignKey('eBayItem', on_delete=models.CASCADE)
    ebay_item_image = models.ImageField(upload_to='imgs')
