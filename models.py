"""
Module holds the object models for the Happy Hour app
"""
import json
import StringIO
import urllib
import pycurl
import config

# API Keys
apikey = config.G_API_KEY
fs_client_id = config.FS_CLIENT_ID
fs_secret = config.FS_CLIENT_SECRET

# gets restaurants from a given location
class User(object):
    """
    User superclass. Stores basic lat / lon data for each user as a comma-separated string value
    """
    def __init__(self):
        self.location = ''

class Place(object):
    """
    Place superclass. Gets various detail attributes from Google Places and
    Foursquare APIs using Curl
    """
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

    @staticmethod
    def get_places(coords, radius='16093'):
        """
        Gets all places within a 10 mile radius of a geo passed in as csv string.
        Returns a list of place objects.
        """
        url = ("https://maps.googleapis.com/maps/api/place/nearbysearch/json?"
               "location=%s&radius=%s&type=restaurant&key=%s" % \
                (urllib.quote_plus(coords), urllib.quote_plus(radius), \
                 urllib.quote_plus(apikey))
              )
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
        place_list = []
        for place in tmp:
            place_id = [place][0].get('place_id')
            # place_list.append([place][0].get('place_id'))
            place_instance = Place(place_id)
            place_list.append(place_instance)
        # length = len(place_list)
        # for i in range(length):
        #     print "*******************************"
        #     print p.website
        #     print p.price_level
            # print place_list[i].rating
            # print place_list[i].name
            # print place_list[i].formatted_address
            # print place_list[i].formatted_phone_number
            # print place_list[i].lat
            # print place_list[i].lng
        return place_list
