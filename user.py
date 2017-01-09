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
        self.lat=''
        self.lng=''
        self.location = str(self.lat) + ',' + str(self.lng)


    def getPlaces(self):
        url = "https://maps.googleapis.com/maps/api/place/nearbysearch/json?location=%s&rankby=distance&type=bar&key=%s" % (
            urllib.quote_plus(self.location), urllib.quote_plus(apikey))
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
        # tmp = places.get('results')
        placeList = []
        for place in places:
            # stores place_id from query
            placeId = [place][0].get('place_id')
            print placeId
            p = Place(placeId)
            placeList.append(p)
        print placeList
        return placeList

    # sample location, Heights Houston
    # getPlaces('29.799592,-95.420138')
    #
    # gets additional info on the given place_id
#     def getInfo(self, loc):
#         url = "https://maps.googleapis.com/maps/api/place/details/json?placeid=%s&key=%s" % (
#             urllib.quote_plus(loc), urllib.quote_plus(apikey))
#         response = StringIO.StringIO()
#         c = pycurl.Curl()
#         c.setopt(c.URL, url)
#         c.setopt(c.WRITEFUNCTION, response.write)
#         c.setopt(c.HTTPHEADER, ['Content-Type: application/json', 'Accept-Charset: UTF-8'])
#         c.setopt(c.POSTFIELDS, '@request.json')
#         c.perform()
#         c.close()
#         info = json.loads(response.getvalue())
#         response.close()
#         return info
#
#     # takes in location and pulls data from getPlaces and getInfo
#     # def getURL(self):
#     #     self.location = str(self.lat) + ',' + str(self.lng)
#     #     print self.location
#     #     places = User.getPlaces(self)
#     #     tmp = places.get('results')
#     #     for place in tmp:
#     #         # stores place_id from query
#     #         placeList = []
#     #         placeList.append([place][0].get('place_id'))
#
#             # lat = [place][0].get('geometry').get('location').get('lat')
#             # lng = [place][0].get('geometry').get('location').get('lng')
#             # runs query to get additional info from the place_id
#             # info = User.getInfo(self, [place][0].get('place_id'))
#             # store website url
#             # tmp_web = str(info.get('result').get('website'))
#             # stores urls into a list
#
#             # todo scrape tmp_web sites for keywords
#
class Place:
    def __init__(self, place_id):
        self.place_id=place_id
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
        # lat = [place][0].get('geometry').get('location').get('lat')
        # lng = [place][0].get('geometry').get('location').get('lng')
        self.web = str(info.get('result').get('website'))
