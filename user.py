import config
import json
import pycurl
import StringIO
import urllib
import sys
from flask import Flask

# google API key
apikey = config.apikey

# testing merge

# gets restaurants from a given location
class User:
    def __init__(self):
        self.location = {}
        self.place_id = ''
        self.loc = {}

    def getPlaces(self):
        url = "https://maps.googleapis.com/maps/api/place/nearbysearch/json?location=%s&rankby=distance&type=restaurant|bar&key=%s" % (
            urllib.quote_plus(self.location), urllib.quote_plus(apikey))
        response = StringIO.StringIO()
        c = pycurl.Curl()
        c.setopt(c.URL, url)
        c.setopt(c.WRITEFUNCTION, response.write)
        c.setopt(c.HTTPHEADER, ['Content-Type: application/json', 'Accept-Charset: UTF-8'])
        c.setopt(c.POSTFIELDS, '@request.json')
        c.perform()
        c.close()
        self.places = json.loads(response.getvalue())
        response.close()
        return self.places

    # sample location, Heights Houston
    # getPlaces('29.799592,-95.420138')
    #
    # gets additional info on the given place_id
    def getInfo(self):
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
        self.info = json.loads(response.getvalue())
        response.close()
        return self.info

    # takes in location and pulls data from getPlaces and getInfo
    def getURL(self, loc):
        self.location = str(loc['latitude']) + ',' + str(loc['longitude'])
        print self.location
        places = User.getPlaces(self)
        tmp = places.get('results')
        for place in tmp:
            # stores place_id from query
            self.place_id = [place][0].get('place_id')
            self.lat = [place][0].get('geometry').get('location').get('lat')
            self.lng = [place][0].get('geometry').get('location').get('lng')
            # runs query to get additional info from the place_id
            info = User.getInfo(self)
            # store website url
            tmp_web = info.get('result').get('website')
            print tmp_web

            # todo scrape tmp_web sites for keywords
