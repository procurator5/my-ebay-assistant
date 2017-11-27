from django.contrib import admin
from .models import Species, Scpecies2Item, stopWords
from django.conf.urls import url
import re
import json

from ebay_parse.models import Setting, eBayItem, eBayCategory

from django.http import HttpResponseRedirect, HttpResponse
from django.core.urlresolvers import reverse
from googletrans import Translator

# Register your models here.
class SpeciesAdmin(admin.ModelAdmin):
    list_display = ('species_name', 'species_first_name', 'species_photo_img', 'category')
    change_list_template = 'admin/species/species/change_list.html'
    #: resource class
    resource_class = None
    #: import data encoding
    from_encoding = "utf-8"
    skip_admin_log = None
    # storage class for saving temporary files
    tmp_storage_class = None

    def get_model_info(self):
        # module_name is renamed to model_name in Django 1.8
        app_label = self.model._meta.app_label
        try:
            return (app_label, self.model._meta.model_name,)
        except AttributeError:
            return (app_label, self.model._meta.module_name,)    

    def get_urls(self):
        urls = super(SpeciesAdmin, self).get_urls()
        info = self.get_model_info()
        my_urls = [
            url(r'^import/$',
                self.admin_site.admin_view(self.import_action),
                name='%s_%s_import' % info),
            url(r'^test/$',
                self.admin_site.admin_view(self.test_action),
                name='%s_%s_test' % info),
        ]
        return my_urls + urls

    def import_action(self, request, *args, **kwargs):
        # custom view which should return an HttpResponse
        translator = Translator()
        items = eBayItem.getUndefinedItems()
        for item in items:
            species = Species.findSpeciesRelation(item)
            if species == None:
                try:
                    russian = translator.translate(item.ebay_item_title, dest='ru', src='en')
                except json.decoder.JSONDecodeError as e:
                    self.message_user(request, str(e))
                    break
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
                        species = Species(species_name = russian, category = item.ebay_category, species_photo = item.ebay_gallery_icon)
                        print(russian)
                        species.save()
                        relation = Scpecies2Item(species = species, item = item)
                        relation.save()
            else:
                relation = Scpecies2Item(species = species, item = item)
                relation.save()
                    

        self.message_user(request, 'Loaded success...')  
        row_count = Species.deleteDublicates()

        self.message_user(request, 'Delete %d dublicate rows' % row_count )  
                
        url = reverse('admin:%s_%s_changelist' % self.get_model_info(),
                          current_app=self.admin_site.name)
        return HttpResponseRedirect(url)
    
    def test_action(self, request, *args, **kwargs):
        row_count = Species.deleteDublicates()

        self.message_user(request, 'Delete %d dublicate rows' % row_count )  
        
        url = reverse('admin:%s_%s_changelist' % self.get_model_info(),
                          current_app=self.admin_site.name)
        return HttpResponseRedirect(url)       

admin.site.register(Species, SpeciesAdmin)
admin.site.register(stopWords,
                        list_display=(
                            'word',
                        )
                    )
