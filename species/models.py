from django.db import models
from django.db.models.fields.related import ForeignKey
from django.db.models.fields import CharField
from django.db import connection

from django.db.models.fields.files import ImageField

# Create your models here.

class Species(models.Model):
    species_name = CharField(max_length = 256) 
    species_first_name = CharField(max_length = 128)
    species_last_name = CharField(max_length = 128)
    category = ForeignKey('ebay_parse.eBayCategory', on_delete=models.CASCADE)
    
    species_photo = ImageField(blank=True, upload_to='species')
    
    def getSpeciesDetailInfo(species_id):
        cursor = connection.cursor()
        cursor.execute("""
        WITH info as(
            select ss.id, count(*), avg(ebay_item_price), min(ebay_item_price), max(ebay_item_price) from species_species ss
            join species_scpecies2item si ON ss.id=si.species_id
            join ebay_parse_ebayitem pe ON pe.ebay_item_id = si.item_id
            group by ss.id)
            select * from species_species ss 
            JOIN info USING(id)
            JOIN ebay_parse_ebaycategory ec ON ec.ebay_category_id = ss.category_id
            WHERE id = %s
            """, [species_id])
        return dictfetchall(cursor)
    
    def best_image(self):
        cursor = connection.cursor()
        cursor.execute("""
           select ebay_item_image
                from species_species ss
                join species_scpecies2item si ON ss.id=si.species_id
                join ebay_parse_ebayitem pe ON pe.ebay_item_id = si.item_id
                join ebay_parse_ebayitemgallery ei USING(ebay_item_id)
                where ss.id = 90
                limit 1;

            """, [self.id])
        return cursor.fetch()[0]
    
    def save(self):
        if self.species_photo is None:
            self.species_photo = self.best_image()
        super(Species, self).save()
        
    getSpeciesDetailInfo = staticmethod(getSpeciesDetailInfo)
    
    
class Scpecies2Item(models.Model):
    species = ForeignKey('Species', on_delete=models.CASCADE)
    item = ForeignKey('ebay_parse.eBayItem', on_delete=models.CASCADE)

class stopWords(models.Model):
    word = CharField(max_length = 256)
    
    
def dictfetchall(cursor):
    "Returns all rows from a cursor as a dict"
    desc = cursor.description
    return [
        dict(zip([col[0] for col in desc], row))
        for row in cursor.fetchall()
    ]
