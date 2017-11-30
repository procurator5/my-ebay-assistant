from django.contrib import admin
from .models import Species, Scpecies2Item, stopWords
from django.conf.urls import url

from ebay_parse.models import eBayItem

from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse

import re

# Register your models here.
class SpeciesAdmin(admin.ModelAdmin):
    list_display = ('species_name', 'species_first_name', 'species_last_name', 'species_photo_img', 'show_category')
    list_filter = [ 'category__ebay_category_name' ] 
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
        items = eBayItem.getUndefinedItems()
        for item in items:
            species = Species.findSpeciesRelation(item)
            if species == None:
                genuses = Species.findGenusByDescription(item.ebay_item_title)
                # We have 2 options:
                # 1. We know genus of the item
                if genuses:
                    rFilter = re.compile(u"""[\'\.\-\,\!\"\№\;\%\:\?\@\$\^\*\&\(\)\_\+]""")
                    ebay_item_title = rFilter.sub(' ', item.ebay_item_title.lower() )
                    rFilterSpace = re.compile(u"""[\ ]{1,}""")
                    ebay_item_title = rFilterSpace.sub(' ', ebay_item_title )                    
                    words = ebay_item_title.split()
                    genus = genuses[0][0]
                    print("1> " +genus)
                    print(words)
                    try:
                        sp = words[words.index(genus)+1]
                    except IndexError:
                        sp='sp'
                        
                    print("1> " +genus + " "+ sp)
                    if not Species.objects.filter(species_name = genus + " "+ sp).exists():
                        species = Species(species_name = genus + " "+ sp, category = item.ebay_category, species_photo = item.ebay_gallery_icon, species_first_name = genus)
                        species.save()
                    else:
                        species = Species.objects.filter(species_name = genus + " "+ sp).first()
                    relation = Scpecies2Item(species = species, item = item)
                    relation.save()
                # 2. We know nothing
                else:
                    species =Species()
                    species.saveUnknownSpecies(item)
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
