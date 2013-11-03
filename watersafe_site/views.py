#Create your views here.
from models import *
from django.shortcuts import render_to_response
from django.template import RequestContext, loader
from datetime import timedelta, date
import json, urllib, httplib2
from api_keys import *
import datamodel

http = httplib2.Http()

def do_GET(url):
  body = {}
  headers = {'Content-type': 'application/x-www-form-urlencoded'}
  response, content = http.request(url, 'GET', headers=headers, body=urllib.urlencode(body))
  return content



def Contact(address):
  address = address.replace(' ','+')
  url = 'https://cicero.azavea.com/v3.1/official?search_address='+address+'&search_country=US&user=watersafe&key='+cicero_api_key
  body = {}
  headers = {'Content-type': 'application/json'}
  response, content = http.request(url, 'GET', headers=headers, body=urllib.urlencode(body))
  return content

def search_form(request):
  return render_to_response('index.html', context_instance=RequestContext(request))

def LearnMore(request):
  return render_to_response('learn_more.html', context_instance=RequestContext(request))

def Search(request):
  if 'address' in request.POST:
    address = request.POST['address']
  else: 
    address = "20 N. 3rd St Philadelphia"
  
  '''
  contact_results = json.loads(Contact(address))
  senator1 = contact_results['response']['results']['candidates'][0]['officials'][1]
  senator2 = contact_results['response']['results']['candidates'][0]['officials'][2]
  governor = contact_results['response']['results']['candidates'][0]['officials'][4]
  representative = contact_results['response']['results']['candidates'][0]['officials'][11]
  '''
  county_code = datamodel.get_county_code_by_address(address)
  ranking_info = datamodel.get_ranking_info_by_county(county_code)
  pws_info = datamodel.get_pws_details_by_county(county_code)

  if ranking_info['bucket'] == "G":
    rating_type = "green-rating"
    rating_button = "green-button"
  elif ranking_info['bucket'] == "Y":
    rating_type = "yellow-rating"
    rating_button = "yellow_button"
  else: 
    rating_type = "red-rating"
    rating_button = "red_button"

  return render_to_response('results.html', {
      'county_id': county_code, 
      'address': address,
      'incident_count': ranking_info['incident_count'],
      'bucket': ranking_info['bucket'],
      'rank': ranking_info['rank'],
      'rating_type': rating_type,
      'rating_button': rating_button,
      'pws_info': pws_info
  }, context_instance=RequestContext(request))
