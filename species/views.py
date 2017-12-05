from django.http import HttpResponse
from django.template import loader
from django.db.models import Count

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
                'species' : Species.objects.filter(category=eCategory).order_by('species_first_name').values('species_first_name').annotate(dcount=Count('species_first_name')),
                'nodes': eBayCategory.objects.all(),
                'category': eCategory,
                }
    return HttpResponse(template.render(context, request))

def genus(request, genus_id):
    template = loader.get_template("species/genus.html")
    eCategory = Species.objects.filter(species_first_name = genus_id).first().category
    context = {
                'species' : Species.objects.filter(category=eCategory, species_first_name = genus_id).order_by('species_name').all(),
                'nodes': eBayCategory.objects.all(),
                'category': eCategory,
                'genus': genus_id,
                'stat':Species.getGenusStatistics(genus_id)
                }
    return HttpResponse(template.render(context, request))

def search(request):
    query = request.GET['q']
    template = loader.get_template("species/category.html")

    context = {
                'species' : Species.objects.search(query),
                'nodes': eBayCategory.objects.all(),
                }
    return HttpResponse(template.render(context, request))

def species(request, species_id):
    template = loader.get_template("species/species.html")
    eCategory = Species.objects.get(id = species_id).category
    print(Species.getSpeciesDetailInfo(species_id))
    context = {
                'info' : Species.getSpeciesDetailInfo(species_id),
                'nodes': eBayCategory.objects.all(),
                'category': eCategory,
                'items': eBayItem.getItemsForSpecies(species_id)
                }
    return HttpResponse(template.render(context, request))
