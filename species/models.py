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
    
    def getSpeciesDetailInfo(specie_id):
        return Species.objects.raw("""
        WITH info as(
            select ss.id, count(*), avg(ebay_item_price), min(ebay_item_price), max(ebay_item_price) from species_species ss
            join species_scpecies2item si ON ss.id=si.species_id
            join ebay_parse_ebayitem pe ON pe.ebay_item_id = si.item_id
            group by ss.id)
            select * from species_species ss 
            JOIN info USING(id)
            JOIN ebay_parse_ebaycategory ec ON ec.ebay_category_id = ss.category_id            
            WHERE id = %s
        """, params=[specie_id])
        
    getSpeciesDetailInfo = staticmethod(getSpeciesDetailInfo)
    
class Scpecies2Item(models.Model):
    species = ForeignKey('Species', on_delete=models.CASCADE)
    item = ForeignKey('ebay_parse.eBayItem', on_delete=models.CASCADE)

class stopWords(models.Model):
    word = CharField(max_length = 256)
