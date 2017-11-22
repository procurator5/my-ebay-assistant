from django.shortcuts import render
from django.http import HttpResponse
from django.template import loader

from ebay_parse.models import eBayCategory, eBayItem
from .models import Species

# Create your views here.
def index(request):
    template = loader.get_template("species/index.html")
    context = {
                'nodes': eBayCategory.objects.all(),
                }
    return HttpResponse(template.render(context, request))

def category(request, category_id):
    template = loader.get_template("species/category.html")
    eCategory = eBayCategory.objects.get(ebay_category_id = category_id)
    context = {
                'species' : Species.objects.filter(category=eCategory).order_by('species_name'),
                'nodes': eBayCategory.objects.all(),
                'category': eCategory,
                }
    return HttpResponse(template.render(context, request))

def species(request, species_id):
    template = loader.get_template("species/species.html")

    context = {
                'info' : Species.getSpeciesDetailInfo(species_id)[0],
                'nodes': eBayCategory.objects.all(),
                'items': eBayItem.getItemsForSpecies(species_id)
                }
    return HttpResponse(template.render(context, request))
