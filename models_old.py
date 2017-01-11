"""
Module holds the object models for the Happy Hour app
"""
import json
import StringIO
import urllib
import pycurl
import config

# API Keys
APIKEY = config.G_API_KEY
FS_CLIENT_ID = config.FS_CLIENT_ID
FS_SECRET = config.FS_CLIENT_SECRET

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
        # Curl to get place details from Google
        url = "https://maps.googleapis.com/maps/api/place/details/json?placeid=%s&key=%s" % (
            urllib.quote_plus(self.place_id), urllib.quote_plus(APIKEY))
        g_place_deets = ApiConnect.get_load(url)
        self.lat = str(g_place_deets.get('result').get('geometry').get('location').get('lat'))
        self.lng = str(g_place_deets.get('result').get('geometry').get('location').get('lng'))
        self.website = str(g_place_deets.get('result').get('website'))
        self.price_level = str(g_place_deets.get('result').get('price_level'))
        self.rating = str(g_place_deets.get('result').get('rating'))
        self.name = str(g_place_deets.get('result').get('name'))
        self.formatted_phone_number = str(g_place_deets.get('result').get('formatted_phone_number'))
        self.formatted_address = str(g_place_deets.get('result').get('formatted_address'))

        # Curl to get Foursquare venue ID
        url = ("https://api.foursquare.com/v2/venues/search?intent=match&ll=%s"
               "&query=%s&client_id=%s&client_secret=%s&v=20170109" % \
               (urllib.quote_plus(self.lat + ',' + self.lng), \
                urllib.quote_plus(self.name), \
                urllib.quote_plus(FS_CLIENT_ID), \
                urllib.quote_plus(FS_SECRET)
               )
              )
        fs_venue_search = ApiConnect.get_load(url)
        if len(fs_venue_search.get('response').get('venues')) > 0:
            self.fs_venue_id = str(fs_venue_search.get('response').\
            get('venues')[0].get('id', '0'))
        else:
            self.fs_venue_id = '0'
        # Curl to get Foursquare happy hour menu description
        url = ("https://api.foursquare.com/v2/venues/%s/menu?client_id=%s&client_"
               "secret=%s&v=20170109" % \
               (urllib.quote_plus(self.fs_venue_id), \
                urllib.quote_plus(FS_CLIENT_ID), \
                urllib.quote_plus(FS_SECRET)
               )
              )
        fs_venue_deets = ApiConnect.get_load(url)
        self.happy_string = ''
        for menu in fs_venue_deets.get('response').get('menu').get('menus')\
        .get('items', [{'name': '', 'description': ''}]):
            if 'happy hour' in str(menu.get('name', '')).lower() or \
            'happy hour' in str(menu.get('description', '')).lower():
                self.happy_string = menu.get('description').lower()
                break
        print 'name: %s' % self.name
        print 'happy_string:'
        print '---> %s' % self.happy_string

    @staticmethod
    def get_places(coords, radius='1600'):
        """
        Gets all places within a certain meter radius of a geo passed in as csv
        string. Default radius is one mile in meters. Returns a list of place
        objects.
        """
        url = ("https://maps.googleapis.com/maps/api/place/nearbysearch/json?"
               "location=%s&radius=%s&type=restaurant&key=%s" % \
               (coords, urllib.quote_plus(radius), \
                 urllib.quote_plus(APIKEY))
              )
        places_list = ApiConnect.get_load(url).get('results')
        place_objects_list = []
        for place in places_list:
            place_id = [place][0].get('place_id')
            place_instance = Place(place_id)
            place_objects_list.append(place_instance)
        return place_objects_list

class ApiConnect(object):
    """
    Holds Curl procedures to get info from our API partners
    """
    @staticmethod
    def get_load(api_call):
        """
        Performs Curl with PyCurl using the GET method. Opens/closes each conn.
        Args: Full URL for the API call
        Returns: getvalue of JSON load from API
        """
        response = StringIO.StringIO()
        c = pycurl.Curl()
        c.setopt(c.URL, api_call)
        c.setopt(c.WRITEFUNCTION, response.write)
        c.setopt(c.HTTPHEADER, ['Content-Type: application/json', 'Accept-Charset: UTF-8'])
        c.perform()
        c.close()
        json_values = json.loads(response.getvalue())
        response.close()
        return json_values