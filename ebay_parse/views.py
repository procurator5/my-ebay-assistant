from django.http import HttpResponse
from django.template import loader
from django.core.files.images import ImageFile
from django_cron import CronJobBase, Schedule

import os
import json 
from lxml import etree
import urllib.request

from .models import *
from fileinput import filename
from species.models import Species, Scpecies2Item

import logging
from django.http.response import HttpResponseRedirect
from django.template.context_processors import request


def category(request, category_id):

    if request.user.is_authenticated():                                
        template = loader.get_template("ebay_parse/category.html")
        page = int(request.GET.get('page', 1 ))
        if page < 1:
            page = 1

        context = {
                    'category': eBayCategory.objects.get(ebay_category_id = category_id),
                    'nodes': eBayCategory.objects.filter(ebay_category_enabled = True),
                    'items': eBayItem.getUndefinedItems(category_id, 100, ( page - 1 ) * 100),
                    'pages': range(1, eBayItem.getUndefPagesCount(category_id, 100)),
                    }
        return HttpResponse(template.render(context, request))
    return HttpResponseRedirect("/")

def saveSpecies(request):
    genus = request.GET['genus'].lower()
    species = request.GET['species'].lower()
    category_id = request.GET['category_id']
    if request.user.is_authenticated():
        template = loader.get_template("ebay_parse/save.html")
        items = eBayItem.objects.search(genus + " "+ species)
        print(items.all())
        if len(items) > 0:
            sp = Species(species_name = genus + " "+ species, species_first_name = genus, species_last_name = species)
            sp.category = eBayCategory.objects.get(ebay_category_id = int(category_id))
            sp.save()
            for item in items:
                rel = Scpecies2Item(species = sp, item = item)
                rel.save()

            sp.species_photo = sp.best_image()
            sp.save()
        context = {
                    'category': eBayCategory.objects.get(ebay_category_id = category_id),
                    'nodes': eBayCategory.objects.filter(ebay_category_enabled = True),
                    'items': items,
                    'genus': genus,
                    'species': species,
                    }
        return HttpResponse(template.render(context, request))
    else:
        return HttpResponseRedirect("/")

def deleteItem(request, item_id):
    if request.user.is_authenticated():
        eBayItem.objects.get(ebay_item_id = item_id).delete()
        return HttpResponse("OK")            
    return HttpResponse("Error")

def loadCategory(request, category_id):    
    if request.user.is_authenticated():                                
        template = loader.get_template("ebay_parse/load_category.html")
        
        l = AutoLoadItems(request)
        l.loadOnlyOneCategory(category_id)
    
        #Вычисляем, что надо подгрузить
        proceseedItems = eBayItem.objects.filter(ebay_item_description = None, ebay_category = l.category).all()
    
        context = {'all_items': l.all_items, 
                    'loaded_items': l.all_items - l.loaded_items,
                    'category_name': l.category.ebay_category_name,
                    'nodes': eBayCategory.objects.filter(ebay_category_enabled = True),
                    'proceseed_items': proceseedItems,
                    'proceseed_items_count': proceseedItems.count(),
                    'pages': l.pages,
                    }
        return HttpResponse(template.render(context, request))
    return HttpResponseRedirect("/")

# Create your views here.
def index(request):
    if request.user.is_authenticated():
        template = loader.get_template("ebay_parse/index.html")
        context = {
                    'nodes': eBayCategory.objects.filter(ebay_category_enabled = True),
                    'items': eBayItem.getUndefinedItems(),
                    }
        return HttpResponse(template.render(context, request))
    return HttpResponseRedirect("/")


def getItem(request, item_id):
    l = AutoLoadItems()
    item = eBayItem.objects.get(ebay_item_id = item_id)
    res = l.saveSingleItem(item)
    return HttpResponse(str(res))

def get_response(operation_name, data, encoding, **headers):
    globalId = 'EBAY-US'
    # take app_name from database

    app_name = Setting.getValue('AppID')
    endpoint = 'http://svcs.ebay.com/services/search/FindingService/v1'

    http_headers = {
        "X-EBAY-SOA-OPERATION-NAME": operation_name,
        "X-EBAY-SOA-SECURITY-APPNAME": app_name,
        "X-EBAY-SOA-GLOBAL-ID": globalId,
        "X-EBAY-SOA-RESPONSE-DATA-FORMAT": encoding}

    http_headers.update(headers)
    try:
        req = urllib.request.Request(endpoint, data, http_headers)
        res = urllib.request.urlopen(req)
    except Exception as e:
        return str(e)
    data = res.read()
    return data

class AutoLoadItems(CronJobBase):
    
    def __init__(self, req = None):
        try:
            RUN_EVERY_MINS = Setting.getIntValue('RunEveryMinLoad')
        except  Exception:
            RUN_EVERY_MINS = 120
            
        self.schedule = Schedule(run_every_mins=RUN_EVERY_MINS)
        self.request = req
            
    code = 'ebay_parse.AutoLoadItems'
    logger = logging.getLogger(__name__)

    #all processed items
    all_items = 0
    #new items
    loaded_items = 0 
    err_items = 0
    pages = 0
    entries = 0
    
    def loadOnlyOneCategory(self, category_id, force = False):
        
        #for logging actions
        from django.contrib.admin.models import LogEntry, CHANGE, ContentType
        
        response = self.findItemsByCategory(categoryId=str(category_id))
        api_resp = json.loads(response.decode('utf-8'))
        items = api_resp['findItemsByCategoryResponse'][0]['searchResult'][0]['item']
    
        self.category = eBayCategory.objects.get(ebay_category_id=int(items[0]['primaryCategory'][0]['categoryId'][0]))
        
        self.pages = int(api_resp['findItemsByCategoryResponse'][0]['paginationOutput'][0]['totalPages'][0])    
        
        for i in range(self.pages):
            self.getOnePageFromCategory( i+1 )
            
        #Загружаем детальную информацию
        if force:
            for item in eBayItem.objects.filter(ebay_item_description = None, ebay_category = self.category).all():
                if not self.saveSingleItem(item):
                    self.err_items += 1
        
        user_id = 1
        if self.request != None:
            user_id = self.request.user.id  
        LogEntry.objects.log_action(
            user_id=user_id,
            content_type_id=ContentType.objects.get_for_model(eBayCategory).pk,
            object_repr=' Load items for category %s. Processed items: %d, loaded items: %d. Errors: %d' % (self.category.ebay_category_name, self.all_items, self.loaded_items, self.err_items),            
            object_id=self.category.ebay_category_id,
            action_flag=CHANGE,
            change_message='Load items from category %s. Processed items: %d, loaded items: %d. Errors: %d' % (self.category.ebay_category_name, self.all_items, self.loaded_items, self.err_items)
        )
                
    def do(self):
        self.all_items = 0
        self.loaded_items = 0
        self.err_items = 0
        for category in eBayCategory.objects.filter(ebay_category_enabled = True).all():
            self.category = category
            self.loadOnlyOneCategory(self.category.ebay_category_id, True)

    def getSingleItem(self, item_id, include_selector=None, encoding="JSON"):
        user_params = {
            'callname': 'GetSingleItem',
            'responseencoding': encoding,
            'ItemID': item_id,
            'version': 967,
            'IncludeSelector': 'Details, TextDescription,ItemSpecifics'
            }
    
        if include_selector:
            user_params['IncludeSelector'] = include_selector
            
        app_id = Setting.getValue('AppID')
        version = 967
        endpoint = 'http://open.api.ebay.com/shopping?'
    
        d = dict(appid=app_id, siteid=0, version=version)
    
        d.update(user_params)
    
        try:
            req = urllib.request.Request(endpoint + urllib.parse.urlencode(d), method='GET')
            res = urllib.request.urlopen(req)
        except Exception as e:
            return str(e)
        data = res.read()
        return data

    def saveSingleItem(self, item):
        response = self.getSingleItem(item.ebay_item_id)
        content = json.loads(response.decode('utf-8'))
        if item.ebay_item_description == None:
            for img in content['Item']['PictureURL']:
                try:
                    row = eBayItemGallery(ebay_item = item  )
                    result = urllib.request.urlretrieve(str(img))       
                    row.save()
                    filename = os.path.basename(str(img))
                    row.ebay_item_image.save(filename[:filename.find('?')],ImageFile(open(result[0], 'rb')))
                    row.save()
                    os.remove(result[0])
                except urllib.error.URLError as e:
                    self.logger.warning(str(e))
                    return False
                
            item.ebay_item_description = content['Item']['Description']
            item.save()
            return True

    def getOnePageFromCategory(self, pageNumber):
        response = self.findItemsByCategory(categoryId=str(self.category.ebay_category_id), paginationInput = {'entriesPerPage': "100",
                                                                                       'pageNumber': str(pageNumber)})
        api_resp = json.loads(response.decode('utf-8'))
        items = api_resp['findItemsByCategoryResponse'][0]['searchResult'][0]['item']
       
        for item in items:
            self.all_items += 1
            #Проверяем есть ли уже такая запись
            if eBayItem.objects.filter(ebay_item_id = int(item['itemId'][0])).exists():
                self.loaded_items +=1
            try:
                watch_count = int(item['listingInfo'][0]['watchCount'][0])
            except KeyError:
                watch_count = 0
    
            try:
                postalcode = str(item['postalCode'][0])
            except KeyError:
                postalcode = 0
                
            try:
                price = float(item['sellingStatus'][0]['currentPrice'][0]['__value__'])
            except KeyError:
                price = 0
    
            try:
                shipping_price = float(item['shippingInfo'][0]['shippingServiceCost'][0]['__value__'])
            except KeyError:
                shipping_price = 0
    
            try:
                method = eBayPaymentMethod.objects.get(payment_method_name=str(item['paymentMethod'][0]))
            except eBayPaymentMethod.DoesNotExist:
                method = eBayPaymentMethod(payment_method_name=str(item['paymentMethod'][0]))
                method.save()
    
            try:
                country = Country.objects.get(country_name=str(item['country'][0]))
            except Country.DoesNotExist:
                country = Country(country_name=str(item['country'][0]))
                country.save()
    
            try:
                listing = ListingType.objects.get(listing_type_name=str(item['listingInfo'][0]['listingType'][0]))
            except ListingType.DoesNotExist:
                listing = ListingType(listing_type_name=str(item['listingInfo'][0]['listingType'][0]))
                listing.save()
            
            row = eBayItem(ebay_item_id=int(item['itemId'][0]))
            if eBayItem.objects.filter(ebay_item_id = int(item['itemId'][0])).exists():
                row.refresh_from_db()
            row.ebay_item_title=str(item['title'][0])
            row.ebay_item_postalcode=postalcode
            row.ebay_item_price=price
            row.ebay_item_shipping_price=shipping_price
            row.ebay_category = self.category
            row.ebay_item_starttime=str(item['listingInfo'][0]['startTime'][0])
            row.ebay_item_endtime=str(item['listingInfo'][0]['endTime'][0])
            row.ebay_watch_count=watch_count
            row.ebay_item_url=str(item['viewItemURL'][0])
            row.ebay_item_location=str(item['location'][0])
            row.country=country
            row.payment_method=method
            row.listing_type=listing
            row.save()
            try:
                row.loadIcon(str(item['galleryURL'][0]))
            except KeyError:
                pass
            if not row.relationIsExists():
                sp = Species.findSpeciesRelation(row)
                if sp != None:
                    relation = Scpecies2Item(species = sp, item = row)
                    relation.save()        

    def findItemsByCategory(
            self,
            categoryId, affiliate=None,
            buyerPostalCode=None, sortOrder=None,
            paginationInput=None, aspectFilter={},
            domainFilter={}, itemFilter={},
            outputSelector={}, encoding="JSON"):
        root = etree.Element("findItemsByCategory",
                             xmlns="http://www.ebay.com/marketplace/search/v1/services")
    
        categoryId_elem = etree.SubElement(root, "categoryId")
        categoryId_elem.text = categoryId
    
        # affiliate is a dict
        if affiliate:
            affiliate_elem = etree.SubElement(root, "affiliate")
            for key in affiliate:
                key_elem = etree.SubElement(affiliate_elem, key)
                key_elem.text = affiliate[key]
    
        if buyerPostalCode:
            buyerPostalCode_elem = etree.SubElement(root, "buyerPostalCode")
            buyerPostalCode_elem.text = buyerPostalCode
    
        # paginationInput is a dict
        if paginationInput:
            paginationInput_elem = etree.SubElement(root, "paginationInput")
            for key in paginationInput:
                key_elem = etree.SubElement(paginationInput_elem, key)
                key_elem.text = paginationInput[key]
    
        # itenFilter is a list of dicts
        for item in itemFilter:
            itemFilter_elem = etree.SubElement(root, "itemFilter")
            for key in item:
                key_elem = etree.SubElement(itemFilter_elem, key)
                key_elem.text = item[key]
    
        # sortOrder
        if sortOrder:
            sortOrder_elem = etree.SubElement(root, "sortOrder")
            sortOrder_elem.text = sortOrder
    
        # aspectFilter is a list of dicts
        for item in aspectFilter:
            aspectFilter_elem = etree.SubElement(root, "aspectFilter")
            for key in item:
                key_elem = etree.SubElement(aspectFilter_elem, key)
                key_elem.text = item[key]
    
        # domainFilter is a list of dicts
        for item in domainFilter:
            domainFilter_elem = etree.SubElement(root, "domainFilter")
            for key in item:
                key_elem = etree.SubElement(domainFilter_elem, key)
                key_elem.text = item[key]
    
        # outputSelector is a list
        for item in outputSelector:
            outputSelector_elem = etree.SubElement(root, "outputSelector")
            outputSelector_elem.text = item
    
        request = etree.tostring(root, pretty_print=True)
        return get_response("findItemsByCategory", request, encoding)
