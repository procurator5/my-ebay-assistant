from django.db import models
import urllib
import os
from django.core.files.images import ImageFile
# Create your models here.

def load_empty_image():
    return "empty"

class Setting(models.Model):
    setting_name = models.CharField(max_length=128)
    setting_value = models.CharField(max_length=128)
    setting_comment = models.CharField(max_length=256)
    setting_comment.null = True

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

    def loadIcon(self, url):
	    try:
		    print(self.ebay_item_id)
		    myItem = eBayItem.objects.get(pk = self.ebay_item_id)
		    print(myItem.ebay_gallery_icon)
		    if myItem.ebay_gallery_icon == 'empty':
			    result = urllib.request.urlretrieve(url)
			    self.ebay_gallery_icon.save(
				os.path.basename(url),
				ImageFile(open(result[0], 'rb'))
			    )
	    except eBayItem.DoesNotExist:
		    result = urllib.request.urlretrieve(url)
		    self.ebay_gallery_icon.save(
			os.path.basename(url),
			ImageFile(open(result[0], 'rb'))
		    )

class eBayCategory(models.Model):
    ebay_category_id = models.AutoField()
    ebay_category_id.primary_key = True
    ebay_category_name = models.CharField(max_length=256)
    ebay_category_parent = models.ForeignKey('eBayCategory', on_delete=models.DO_NOTHING, null = True, blank = True )

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
