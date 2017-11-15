from django.db import models
from django.db.models.fields.related import ForeignKey
from django.db.models.fields import CharField

from ebay_parse.models import eBayCategory 
from ebay_parse.models import eBayItem

# Create your models here.

class Species(models.Model):
    species_name = CharField(max_length = 256) 
    species_first_name = CharField(max_length = 128)
    species_last_name = CharField(max_length = 128)
    category = ForeignKey('ebay_parse.eBayCategory', on_delete=models.CASCADE)