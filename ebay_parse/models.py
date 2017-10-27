from django.db import models

# Create your models here.

class Setting(models.Model):
    setting_name = models.CharField(max_length=128)
    setting_value = models.CharField(max_length=128)
    setting_comment = models.CharField(max_length=256)
    setting_comment.null = True

class eBayItem(models.Model):
    ebay_item_id = models.BigIntegerField()
    ebay_item_title = models.CharField(max_length=256)
    ebay_category_id = models.IntegerField()
    ebay_item_url = models.URLField()
    payment_method_id = models.IntegerField()
    ebay_item_postalcode = models.IntegerField()
    ebay_item_location = models.CharField(max_length=256)
    country_id = models.IntegerField()
    ebay_item_price = models.DecimalField(max_digits = 5, decimal_places=2)
    ebay_item_shipping_price = models.DecimalField(max_digits = 10, decimal_places=2)
    ebay_item_starttime = models.DateTimeField()
    ebay_item_endtime = models.DateTimeField()
    listing_type_id = models.IntegerField()
    ebay_watch_count = models.IntegerField()

