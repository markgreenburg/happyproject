import config
import json
import pycurl
import StringIO
import urllib
import sys

# google API key
apikey = config.apikey


# gets restaurants from a given location
def getPlaces(location):
    url = "https://maps.googleapis.com/maps/api/place/nearbysearch/json?location=%s&rankby=distance&type=restaurant&key=%s" % (
        urllib.quote_plus(location), urllib.quote_plus(apikey))
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


# sample location, Heights Houston
# getPlaces('29.799592,-95.420138')
#
# gets additional info on the given place_id
def getInfo(place_id):
    url = "https://maps.googleapis.com/maps/api/place/details/json?placeid=%s&key=%s" % (
        urllib.quote_plus(place_id), urllib.quote_plus(apikey))
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


# takes in location and pulls data from getPlaces and getInfo
location = sys.argv[1]
places = getPlaces(location)
tmp = places.get('results')
for place in tmp:
    # stores place_id from query
    place_id = [place][0].get('place_id')
    # runs query to get additional info from the place_id
    info = getInfo(place_id)
    # store website url
    tmp_web = info.get('result').get('website')

    # todo scrape tmp_web sites for keywords
