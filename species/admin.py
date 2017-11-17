from django.contrib import admin
from .models import Species, Scpecies2Item, stopWords
from django.conf.urls import url
import re
import json

from ebay_parse.models import Setting, eBayItem, eBayCategory

from django.http import HttpResponseRedirect, HttpResponse
from django.core.urlresolvers import reverse
from googletrans import Translator
from species.models import stopWords

# Register your models here.
class SpeciesAdmin(admin.ModelAdmin):
    list_display = ('species_name', 'species_first_name','category')
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
        ]
        return my_urls + urls

    def import_action(self, request, *args, **kwargs):
        # custom view which should return an HttpResponse
        translator = Translator()
        items = eBayItem.objects.all().values('ebay_item_title', 'ebay_item_id', 'ebay_category')
        for item in items:
            try:
                russian = translator.translate(item['ebay_item_title'], dest='ru', src='en')
            except json.decoder.JSONDecodeError as e:
                self.message_user(request, str(e), message=messages.ERROR)
            russian = re.sub(r'[^a-zA-Z ]', '', str(russian))
            russian = re.sub(r'^Translatedsrcen destru text', '', russian)
            russian = re.sub(r'pronunciationNone$', '', russian)            
            russian = re.sub(r'\s+', ' ', russian)
            russian = re.sub('^\s', '', russian)
            if russian != '':
                if not Species.objects.filter(species_name = russian).exists():
                    eCategory = eBayCategory.objects.get(ebay_category_id = item['ebay_category'])
                    species = Species(species_name = russian, category = eCategory)
                    species.save()
                    eItem = eBayItem.objects.get(ebay_item_id = item['ebay_item_id'])
                    relation = Scpecies2Item(species = species, item = eItem)
                    relation.save()
                    

        self.message_user(request, 'Loaded success...')  
        url = reverse('admin:%s_%s_changelist' % self.get_model_info(),
                          current_app=self.admin_site.name)
        return HttpResponseRedirect(url)    

admin.site.register(Species, SpeciesAdmin)
admin.site.register(stopWords,
                        list_display=(
                            'word',
                        )
                    )
