from django.db import models
from django.db.models.fields.related import ForeignKey
from django.db.models.fields import CharField
from django.db import connection

#full-text search 
from djorm_pgfulltext.models import SearchManager
from djorm_pgfulltext.fields import VectorField

import re
import json
from googletrans import Translator

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
                where ss.id = %s
                limit 1;

            """, [self.id])
        return cursor.fetch()[0]
    
    def save(self):
        if self.species_photo is None:
            self.species_photo = self.best_image()
        super(Species, self).save()
            
    def saveUnknownSpecies(self, item):
        self.species_name = item.ebay_item_title
        self.category = item.ebay_category
        self.species_photo = item.ebay_gallery_icon
        
        translator = Translator()
        try:
            russian = translator.translate(item.ebay_item_title, dest='ru', src='en')
        except json.decoder.JSONDecodeError as e:
            return
        russian = re.sub(r'[^a-zA-Z ]', '', str(russian))
        russian = re.sub(r'^Translatedsrcen destru text', '', russian)
        russian = re.sub(r'pronunciationNone$', '', russian)            
        russian = re.sub(r'\s+', ' ', russian)
        russian = re.sub('^\s', '', russian)
        russian = russian.lower()
        #delete stop words
        for word in stopWords.objects.all():
            russian = re.sub(word.word.lower(), '', russian)
            if russian != '':
                if not Species.objects.filter(species_name = russian).exists():
                    self.species_name = russian

        print("2> "+self.species_name)                    
        if Species.objects.filter(species_name = self.species_name).exists():
            self.id = Species.objects.filter(species_name = self.species_name).first().id           
            print("2> dublicate " + self.species_name)  
        
        super(Species, self).save()

    
    def species_photo_img(self):
        if self.species_photo:
            return u'<a href="{0}" target="_blank"><img src="{0}" width="100"/></a>'.format(self.species_photo.url)
        else:
            return '(Нет изображения)'
        
    def show_category(self):
        return self.category.ebay_category_name
        
    species_photo_img.short_description = 'Картинка'
    species_photo_img.allow_tags = True    

    def findGenusByDescription(desc):
        cursor = connection.cursor()
        cursor.execute("""
            select DISTINCT lower(species_first_name) 
                from species_species 
                where to_tsvector(%s) @@ to_tsquery(species_first_name);
        """, [desc])
        return cursor.fetchall()

    def findSpeciesRelation(it):
        genuses = Species.findGenusByDescription(it.ebay_item_title)
        for genus in genuses:
            cursor = connection.cursor()
            cursor.execute("""
                select DISTINCT lower(species_last_name) 
                    from species_species 
                    where lower(species_first_name) = %s AND
                        to_tsvector(%s) @@ to_tsquery(species_last_name);
            """, [genus[0].lower(), it.ebay_item_title])
            rows = cursor.fetchall()
            if len(rows) > 0:
                return Species.objects.filter(species_first_name__iexact = genus[0], species_last_name__iexact = rows[0][0]).first()

    
    #удаляет дубликаты в списке видов
    def deleteDublicates():
        #Шаг1 поиск дубликатов (род/вид)
        cursor = connection.cursor()
        cursor.execute("""
           WITH species AS(
                SELECT species_first_name, species_last_name, count(*) AS count
                  FROM species_species
                  GROUP BY species_first_name, species_last_name
            )
            select * from species
                WHERE count >1 ;
            """)
        #перебираем дублированные записи и чистим лишние
        i = 0
        for row in cursor.fetchall():
            species = Species.objects.filter(species_first_name = row[0], species_last_name = row[1]).all()
            for s in species[1:]:
                Scpecies2Item.objects.filter(species = s).update(species= species[0])
                s.delete()
            i = i + 1 
        return i
    
    findGenusByDescription = staticmethod(findGenusByDescription)
    getSpeciesDetailInfo = staticmethod(getSpeciesDetailInfo)
    findSpeciesRelation = staticmethod(findSpeciesRelation)
    deleteDublicates = staticmethod(deleteDublicates)
    
    #full text search
    search_index = VectorField()
    
    objects = SearchManager(
        fields=('species_name', 'species_first_name', 'species_last_name'),
        config='pg_catalog.english',
        search_field='search_index',
        auto_update_search_field=True
    )
        
    
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
