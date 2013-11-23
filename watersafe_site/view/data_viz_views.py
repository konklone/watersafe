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
def historicalMotionChart(request):
    try:
        chartType = request.POST['grouping']
        logger.info('chartType ' + chartType)
        if 'countyId' in request.POST:
            countyid = request.POST['countyId']
        datatablejson = ''
        
        if chartType == 'state':
            responsejson = datamodel.get_state_historic_violations(countyid)
            logger.info(responsejson)
            description =       {"COUNTY": ("string", "County"),
                               "DATE_YEAR": ("number", "Year"),
                               "VIOLATIONS_COUNT": ("number", "# of Violations")
                               }
        elif chartType == 'contaminants':
            responsejson = datamodel.get_county_contaminant_historic_violations(countyid)
            logger.info(responsejson)
            description =       {"CONTAMINANT": ("string", "Contaminant"),
                               "DATE_YEAR": ("number", "Year"),
                   "VIOLATIONS_COUNT": ("number", "# of Violations")
                               }
            
        data_table = gviz_api.DataTable(description)
        data_table.LoadData(responsejson)
        datatablejson = data_table.ToJSon()
    except:
        traceback.print_exc()
        
    return HttpResponse(str(datatablejson))
