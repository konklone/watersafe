#Create your views here.
from datetime import timedelta, date
from django.core.mail import send_mail
from django.core.mail.backends import console
from django.core.mail.message import EmailMultiAlternatives
from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.template import RequestContext, loader
from django.template.context import Context
from django.template.loader import get_template
from django.views.decorators.csrf import csrf_exempt
from watersafe_site.model import datamodel
import httplib2
import json
import logging
import urllib

http = httplib2.Http()
# Get an instance of a logger
logger = logging.getLogger(__name__)
PRIVATE_IPS_PREFIX = ('10.', '172.', '192.', )

def do_GET(url):
  body = {}
  headers = {'Content-type': 'application/x-www-form-urlencoded'}
  response, content = http.request(url, 'GET', headers=headers, body=urllib.urlencode(body))
  return content

def get_client_ip(request):
    """get the client ip from the request
    """
    remote_address = request.META.get('REMOTE_ADDR')
    # set the default value of the ip to be the REMOTE_ADDR if available
    # else None
    ip = remote_address
    # try to get the first non-proxy ip (not a private ip) from the
    # HTTP_X_FORWARDED_FOR
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        proxies = x_forwarded_for.split(',')
        # remove the private ips from the beginning
        while (len(proxies) > 0 and
                proxies[0].startswith(PRIVATE_IPS_PREFIX)):
            proxies.pop(0)
        # take the first ip which is not a private one (of a proxy)
        if len(proxies) > 0:
            ip = proxies[0]

    return ip


def search_form(request):
  return render_to_response('index.html', context_instance=RequestContext(request))

def LearnMore(request):
  return render_to_response('learn_more.html', context_instance=RequestContext(request))


@csrf_exempt
def SendEmail(request):
    subject, from_email = 'Violation Message', 'h2osafeus@gmail.com'
    to = ['vsujith@gmail.com']
    address = '';
    
    if 'reqAddress' in request.POST:
        address = request.POST['reqAddress']
    if 'emailText' in request.POST:
        userEmail = request.POST['emailText']
        to.append(userEmail)
        
    print 'address'+userEmail
    county_code = datamodel.get_county_code_by_address(address)
    pws_info = datamodel.get_pws_details_by_county(county_code)
  
    #Get Template
    emailTemplate     = get_template('email.html')
    data = Context({ 'pws_info': pws_info })
    emailContent = emailTemplate.render(data)
    
    msg = EmailMultiAlternatives(subject, 'Sample', from_email, to)
    msg.attach_alternative(emailContent, "text/html")
    msg.send()
    return HttpResponse(str(0), content_type="text/plain")

@csrf_exempt
def Search(request):
  clientip = get_client_ip(request)
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
  county_code, countyname, state = datamodel.get_county_code_by_address(address)
  logger.info(county_code)
  ranking_info = datamodel.get_ranking_info_by_county(county_code)
  pws_info = datamodel.get_pws_details_by_county(county_code)
  logger.info("client ip " + clientip + " - " + address + " - "+county_code)

  email_id="vsujith@gmail.com"
  #Get Template
  emailTemplate     = get_template('email.html')
  data = Context({ 'pws_info': pws_info })
  emailContent = emailTemplate.render(data)
  
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
      'county_name' :countyname,
      'state' : state,
      'address': address,
      'incident_count': ranking_info['incident_count'],
      'bucket': ranking_info['bucket'],
      'rank': ranking_info['rank'],
      'rating_type': rating_type,
      'rating_button': rating_button,
      'pws_info': pws_info,
      'email_id': email_id,
      'email_content': emailContent,
      'req_address' : address
  }, context_instance=RequestContext(request))
  
  
