import pg
import config
import json
import pycurl
import StringIO
import urllib
import mysql.connector
import sys

apikey = config.apikey

def getPlaces(location):
    url = "https://maps.googleapis.com/maps/api/place/nearbysearch/json?location=%s&rankby=distance&type=restaurant&key=%s" % (urllib.quote_plus(location),urllib.quote_plus(apikey))
    response = StringIO.StringIO()
    c = pycurl.Curl()
    c.setopt(c.URL, url)
    c.setopt(c.WRITEFUNCTION, response.write)
    c.setopt(c.HTTPHEADER, ['Content-Type: application/json', 'Accept-Charset: UTF-8'])
    c.setopt(c.POSTFIELDS, '@request.json')
    c.perform()
    c.close()
    places = json.loads(response.getvalue())
    response.close()
    return places

# getPlaces('29.799592,-95.420138')

def getInfo(place_id):
    url = "https://maps.googleapis.com/maps/api/place/details/json?placeid=%s&key=%s" % (urllib.quote_plus(place_id),urllib.quote_plus(apikey))
    response = StringIO.StringIO()
    c = pycurl.Curl()
    c.setopt(c.URL, url)
    c.setopt(c.WRITEFUNCTION, response.write)
    c.setopt(c.HTTPHEADER, ['Content-Type: application/json', 'Accept-Charset: UTF-8'])
    c.setopt(c.POSTFIELDS, '@request.json')
    c.perform()
    c.close()
    info = json.loads(response.getvalue())
    response.close()
    return info

location = sys.argv[1]
places = getPlaces(location)
print places.get('results')[0].get('place_id')
tmp=places.get('results')
for place in tmp:
    print('************************************')
    place_id = [place][0].get('place_id')
    print('************************************')
    info = getInfo(place_id)
    tmp_web = info.get('result').get('website')
    print tmp_web