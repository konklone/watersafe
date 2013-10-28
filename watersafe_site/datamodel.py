'''
Created on Oct 20, 2013

@author: joekumar
'''
from django.db import connection
import json, urllib, httplib2

http = httplib2.Http()

def do_GET(url):
    body = {}
    headers = {'Content-type': 'application/x-www-form-urlencoded'}
    response, content = http.request(url, 'GET', headers=headers, body=urllib.urlencode(body))
    return content
  
def get_zip_from_address(address):
    encoded_address = urllib.quote(address)  
    url = "http://maps.google.com/maps/api/geocode/json?address={0}&sensor=false".format(encoded_address)
    response = do_GET(url)
    geocode_info = json.loads(response)
    
    if geocode_info['status'] != 'OK':
        print "Status is not OK"
    elif len(geocode_info['results']) == 0:
        print "No results were returned."
    else:
        address_components = geocode_info['results'][0]['address_components']
        for component in address_components:
            if 'postal_code' in component['types']:
                return component['short_name']


def get_county_code_by_address(address):
    zip = get_zip_from_address(address)
    
    cur = connection.cursor()
    try:
        cur.execute('select fips_county_id from zip_county_mapping where zip=%s',[format(zip).upper()])
        countyCode = cur.fetchone()[0]
    finally:
        cur.close()
    return countyCode
    

def get_county_name_by_zip(zipcode):
    query = """
        SELECT CSM.COUNTY_NAME
      FROM COUNTY_STATE_MAPPING CSM, ZIP_COUNTY_MAPPING ZCM
      WHERE CSM.FIPS_COUNTY_ID = ZCM.FIPS_COUNTY_ID
      AND ZCM.ZIP = %s
    """
    cur = connection.cursor()
    try:
        cur.execute(query,[zipcode])
        countyName = cur.fetchone()[0]
    finally:
        cur.close()
    return countyName

def get_ranking_info_by_county(county_code):
    query = """
      SELECT VC.county_id county, SUM(VS.VIOLATION_COUNT) incidents, VC.rank rank, VC.colorcode bucket 
      FROM VIOLATIONS_BY_COUNTY VC, VIOLATION_SUMMARY VS, PWS_COUNTY PWSC
      WHERE VS.PWSID = PWSC.PWSID
      AND PWSC.FIPSCOUNTY = VC.COUNTY_ID
      AND VC.county_id = %s
      AND year(VS.YYYY_MM) >= 2012
      GROUP BY VC.county_id, VC.rank, VC.colorcode
    """
    
    cur = connection.cursor()
    try:
        print query
        cur.execute(query,[county_code])
        #cur.execute(query)
        result = cur.fetchone()
        print result
        county_ranking_info = {}
        county_ranking_info['county_id'] = result[0]
        county_ranking_info['incident_count'] = result[1]
        county_ranking_info['rank'] = result[2]
        county_ranking_info['bucket'] = result[3]
    finally:
        cur.close()
    return county_ranking_info

def dictfetchall(cursor):
    "Returns all rows from a cursor as a dict"
    desc = cursor.description
    return [
        dict(zip([col[0] for col in desc], row))
        for row in cursor.fetchall()
    ]

def get_pws_details_by_county(county_code):

    query = """
      SELECT PWSID pwsid, PWSNAME pws_name, CONTACTCITY contact_city
      , SOURCE_NAME source_long_name, POPULATION_SERVED population_served, PWS_STATUS pws_status, VIOLATION_NAME violation_name
      , CONTAMINANT contaminant, CONTAMINANT_MEASURE contaminant_measure
      FROM VIOLATION_DETAILS_2012
      WHERE COUNTY_ID = %s 
    """
    cur = connection.cursor()
    try:
        cur.execute(query,[county_code])
        result = dictfetchall(cur)
    finally:
        cur.close()
    print result
    return result
