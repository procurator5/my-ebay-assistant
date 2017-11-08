from django.http import HttpResponse
from django.template import loader
from django.core.files.images import ImageFile

import os
import json 
from lxml import etree
import urllib.request

from .models import Country
from .models import ListingType
from .models import Setting
from .models import eBayCategory
from .models import eBayItem
from .models import eBayPaymentMethod
from .models import eBayItemGallery
from fileinput import filename



def category(request, category_id):
    template = loader.get_template("category.html")
    response = findItemsByCategory(categoryId=str(category_id))
    api_resp = json.loads(response.decode('utf-8'))
    items = api_resp['findItemsByCategoryResponse'][0]['searchResult'][0]['item']
    all_items = 0
    loaded_items = 0

    category_name = str(items[0]['primaryCategory'][0]['categoryName'][0])
    cat = eBayCategory(ebay_category_id=int(items[0]['primaryCategory'][0]['categoryId'][0]),
            ebay_category_name=category_name
    )
    cat.save()

   
    for item in items:
        all_items += 1
        #Проверяем есть ли уже такая запись
        if eBayItem.objects.filter(ebay_item_id = int(item['itemId'][0])).exists():
            loaded_items +=1
        try:
            watch_count = int(item['listingInfo'][0]['watchCount'][0])
        except KeyError:
            watch_count = 0

        try:
            postalcode = str(item['postalCode'][0])
        except KeyError:
            postalcode = 0
        price = float(item['sellingStatus'][0]['currentPrice'][0]['__value__'])

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

        row = eBayItem(ebay_item_id=int(item['itemId'][0]),
            ebay_item_title=str(item['title'][0]),
            ebay_item_postalcode=postalcode,
            ebay_item_price=price,
            ebay_item_shipping_price=shipping_price,
            ebay_item_starttime=str(item['listingInfo'][0]['startTime'][0]),
            ebay_item_endtime=str(item['listingInfo'][0]['endTime'][0]),
            ebay_watch_count=watch_count,
            ebay_category=cat,
            ebay_item_url=str(item['viewItemURL'][0]),
            ebay_item_location=str(item['location'][0]),
            country=country,
            payment_method=method,
            listing_type=listing
    )
        row.loadIcon(str(item['galleryURL'][0]))
        row.save()

    context = {'all_items': all_items, 
                'loaded_items': all_items - loaded_items,
                'category_name': category_name,
                'categories': eBayCategory.objects.all(),
                }
    return HttpResponse(template.render(context, request))

# Create your views here.
def index(request):
    template = loader.get_template("index.html")
    context = {
                'categories': eBayCategory.objects.all(),
                }
    return HttpResponse(template.render(context, request))

def getItem(request, item_id):
    response = GetSingleItem(item_id)
    content = json.loads(response.decode('utf-8'))
    myItem = eBayItem.objects.get(pk = item_id)
    if myItem.ebay_item_description == None:
        for img in content['Item']['PictureURL']:
            row = eBayItemGallery(ebay_item = myItem  )
            result = urllib.request.urlretrieve(str(img))       
            row.save()
            filename = os.path.basename(str(img))
            row.ebay_item_image.save(filename[:filename.find('?')],ImageFile(open(result[0], 'rb')))
            row.save()
            os.remove(result[0])
            
        myItem.ebay_item_description = content['Item']['Description']
        myItem.save()
    return HttpResponse(response)

def get_response(operation_name, data, encoding, **headers):
    globalId = 'EBAY-US'
    # take app_name from database

    app_name = Setting.objects.filter(setting_name='AppID').values('setting_value')[0]['setting_value']
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

def GetSingleItem(item_id, include_selector=None, encoding="JSON"):
    user_params = {
        'callname': GetSingleItem.__name__,
        'responseencoding': encoding,
        'ItemID': item_id,
        'version': 967,
        'IncludeSelector': 'Details, TextDescription,ItemSpecifics'
        }

    if include_selector:
        user_params['IncludeSelector'] = include_selector
        
    app_id = Setting.objects.filter(setting_name='AppID').values('setting_value')[0]['setting_value']
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

def findItemsByCategory(
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
    return get_response(findItemsByCategory.__name__, request, encoding)


