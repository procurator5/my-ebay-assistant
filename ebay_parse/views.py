from django.shortcuts import render
from django.http import HttpResponse
import urllib.request
from lxml import etree
from .models import Setting

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

    #affiliate is a dict
    if affiliate:
        affiliate_elem = etree.SubElement(root, "affiliate")
        for key in affiliate:
            key_elem = etree.SubElement(affiliate_elem, key)
            key_elem.text = affiliate[key]

    if buyerPostalCode:
        buyerPostalCode_elem = etree.SubElement(root, "buyerPostalCode")
        buyerPostalCode_elem.text = buyerPostalCode

    #paginationInput is a dict
    if paginationInput:
        paginationInput_elem = etree.SubElement(root, "paginationInput")
        for key in paginationInput:
            key_elem = etree.SubElement(paginationInput_elem, key)
            key_elem.text = paginationInput[key]

    #itenFilter is a list of dicts
    for item in itemFilter:
        itemFilter_elem = etree.SubElement(root, "itemFilter")
        for key in item:
            key_elem = etree.SubElement(itemFilter_elem, key)
            key_elem.text = item[key]

    #sortOrder
    if sortOrder:
        sortOrder_elem = etree.SubElement(root, "sortOrder")
        sortOrder_elem.text = sortOrder

    #aspectFilter is a list of dicts
    for item in aspectFilter:
        aspectFilter_elem = etree.SubElement(root, "aspectFilter")
        for key in item:
            key_elem = etree.SubElement(aspectFilter_elem, key)
            key_elem.text = item[key]

    #domainFilter is a list of dicts
    for item in domainFilter:
        domainFilter_elem = etree.SubElement(root, "domainFilter")
        for key in item:
            key_elem = etree.SubElement(domainFilter_elem, key)
            key_elem.text = item[key]

    #outputSelector is a list
    for item in outputSelector:
        outputSelector_elem = etree.SubElement(root, "outputSelector")
        outputSelector_elem.text = item

    request = etree.tostring(root, pretty_print=True)
    return get_response(findItemsByCategory.__name__, request, encoding)


# Create your views here.
def index(request):
   response = findItemsByCategory(categoryId="123")
   return HttpResponse(response)

def get_response(operation_name, data, encoding, **headers):
    globalId = 'EBAY-US'
    #take app_name from database

    app_name = Setting.objects.filter(setting_name = 'AppID').values('setting_value')[0]['setting_value']
    endpoint = 'http://svcs.sandbox.ebay.com/services/search/FindingService/v1'

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


