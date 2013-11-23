'''
Created on Nov 16, 2013

@author: joekumar
'''
from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.template.context import RequestContext
from watersafe_site.model import datamodel
from django.views.decorators.csrf import csrf_exempt
import gviz_api
import logging
import traceback
logger = logging.getLogger(__name__)

@csrf_exempt
def motionChart(request):
    try:
        countyid = 42089
        if 'countyId' in request.POST:
            countyid = request.POST['countyId']
        datatablej = ''
        responsejson = datamodel.get_state_historic_violations(countyid)
        logger.info(responsejson)
        description =       {"COUNTY": ("string", "County"),
                               "DATE_YEAR": ("number", "Year"),
                   "VIOLATIONS_COUNT": ("number", "# of Violations")
                               }
        data_table = gviz_api.DataTable(description)
        data_table.LoadData(responsejson)
        datatablej = data_table.ToJSon()
    except:
        traceback.print_exc()
        
    return HttpResponse(str(datatablej))

