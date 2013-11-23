'''
Created on Oct 20, 2013

@author: joekumar
'''
from django.db import connection
import json, urllib, httplib2, logging

http = httplib2.Http()
logger = logging.getLogger(__name__)

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
    logger.debug("zip code is " + zip)
    cur = connection.cursor()
    try:
        cur.execute('select fips_county_id, county, state from ZIP_GEO_INFO where zip_code=%s',[format(zip).upper()])
        result = cur.fetchone()
        countyCode = result[0]
        countyName = result[1]
        state = result[2]
    finally:
        cur.close()
    return (countyCode,countyName,state)
    

def get_ranking_info_by_county(county_code):
    query = """
      SELECT VC.county_id county, SUM(VC.VIOLATIONS_COUNT) incidents, VC.rank rank, VC.colorcode bucket 
      FROM VIOLATIONS_BY_COUNTY VC
      WHERE VC.county_id = %s
      GROUP BY VC.county_id, VC.rank, VC.colorcode
    """
    
    cur = connection.cursor()
    try:
        cur.execute(query,[county_code])
        #cur.execute(query)
        result = cur.fetchone()
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

def get_state_historic_violations(county_code):
    query = """
    select vsyc.COUNTY COUNTY , vsyc.YEAR DATE_YEAR , vsyc.VIOLATIONS_COUNT VIOLATIONS_COUNT
    from VIOLATIONS_SUMMARY_YYYY_COUNTY vsyc
    where vsyc.STATE = 
    (select distinct state from ZIP_GEO_INFO where fips_county_id = %s )
    """
    cur = connection.cursor()
    try:
        cur.execute(query,[county_code])
        result = dictfetchall(cur)
    finally:
        cur.close()
    return result

def get_county_contaminant_historic_violations(county_code):
    query = """
    select vch.CNAME CONTAMINANT , CAST(YEAR(VCH.YYYY_MM) AS UNSIGNED) DATE_YEAR  , CAST( SUM(vch.VIOLATION_COUNT) AS UNSIGNED) VIOLATIONS_COUNT
    from VIOLATION_CONTAMINANTS_HISTORICAL vch
    where vch.COUNTYID = %s 
    GROUP BY vch.CNAME , YEAR(VCH.YYYY_MM)
    """
    cur = connection.cursor()
    try:
        cur.execute(query,[county_code])
        result = dictfetchall(cur)
    finally:
        cur.close()
    return result

    
def get_pws_details_by_county(county_code):

    query = """
      SELECT PWSID pwsid, PWSNAME pws_name, CONTACTCITY contact_city
      , SOURCE_NAME source_long_name, POPULATION_SERVED population_served, PWS_STATUS pws_status, VIOLATION_NAME violation_name
      , VIOLATION_DETAILS_2012.CONTAMINANT contaminant, CONTAMINANT_MEASURE contaminant_measure
      , CONTAMINANT_EFFECTS.Health_Effect health_effect
      , COUNT(*) CONTAMINATION_CNT
      FROM VIOLATION_DETAILS_2012 LEFT JOIN CONTAMINANT_EFFECTS ON VIOLATION_DETAILS_2012.CONTAMINANT = CONTAMINANT_EFFECTS.Contaminant
      WHERE COUNTY_ID = %s 
GROUP BY  PWSID , PWSNAME , CONTACTCITY 
      , SOURCE_NAME , POPULATION_SERVED , PWS_STATUS , VIOLATION_NAME 
      , CONTAMINANT , CONTAMINANT_MEASURE 
ORDER BY pws_status, CONTAMINATION_CNT desc     

    """
    cur = connection.cursor()
    try:
        cur.execute(query,[county_code])
        result = dictfetchall(cur)
    finally:
        cur.close()
    return result
