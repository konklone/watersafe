'''
Created on Nov 6, 2013

@author: joekumar
'''
from django.shortcuts import render_to_response
from django.template.context import RequestContext

def handler500(request):
    return render_to_response('HTTP_500_Error.html', context_instance=RequestContext(request))
