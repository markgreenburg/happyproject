import config
import json
import pycurl
import StringIO
import urllib
import sys
from flask import Flask

# google API key
apikey = config.G_API_KEY
fs_client_id = config.FS_CLIENT_ID
fs_secret = config.FS_CLIENT_SECRET


# gets restaurants from a given location
class User:
    def __init__(self):
        self.location = ''

    def getPlaces(self):
        url = "https://maps.googleapis.com/maps/api/place/nearbysearch/json?location=%s&radius=16093&type=restaurant&key=%s" % (
            urllib.quote_plus(self.location), urllib.quote_plus(apikey))
        response = StringIO.StringIO()
        c = pycurl.Curl()
        c.setopt(c.URL, url)
        c.setopt(c.WRITEFUNCTION, response.write)
        c.setopt(c.HTTPHEADER, ['Content-Type: application/json', 'Accept-Charset: UTF-8'])
        c.setopt(c.POSTFIELDS, '@request.json')
        c.perform()
        c.close()
        query = json.loads(response.getvalue())
        response.close()
        places = query
        tmp = places.get('results')
        placeList = []
        for place in tmp:
            placeId = [place][0].get('place_id')
            # placeList.append([place][0].get('place_id'))
            p = Place(placeId)
            placeList.append(p)
        # length = len(placeList)
        # for i in range(length):
        #     print "*******************************"
        #     print p.website
        #     print p.price_level
            # print placeList[i].rating
            # print placeList[i].name
            # print placeList[i].formatted_address
            # print placeList[i].formatted_phone_number
            # print placeList[i].lat
            # print placeList[i].lng
        return placeList


class Place:
    def __init__(self, place_id):
        self.place_id = place_id
        url = "https://maps.googleapis.com/maps/api/place/details/json?placeid=%s&key=%s" % (
            urllib.quote_plus(self.place_id), urllib.quote_plus(apikey))
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
        self.lat = str(info.get('result').get('geometry').get('location').get('lat'))
        self.lng = str(info.get('result').get('geometry').get('location').get('lng'))
        self.website = str(info.get('result').get('website'))
        self.price_level = str(info.get('result').get('price_level'))
        self.rating = str(info.get('result').get('rating'))
        self.name = str(info.get('result').get('name'))
        self.formatted_phone_number = str(info.get('result').get('formatted_phone_number'))
        self.formatted_address = str(info.get('result').get('formatted_address'))
