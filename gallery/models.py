from django.db import models
from ebay_parse.models import eBayItemGallery
from species.models import Species

# Create your models here.
class Gallery(models.Model):
    gallery_name = models.CharField(max_length = 256)
    gallery_prop = models.TextField(blank = True)
    species = models.ForeignKey('species.Species', on_delete=models.CASCADE, null = True, blank = True)
    
class GalleryItem(models.Model):
    gallery = models.ForeignKey('Gallery', on_delete=models.CASCADE)    
    gallery_item = models.ForeignKey('ebay_parse.eBayItemGallery', on_delete=models.CASCADE)