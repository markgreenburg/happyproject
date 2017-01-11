"""
Module holds the object models for the Happy Hour app
"""
import json
import StringIO
import urllib
import pycurl
import config
import pg

# API Keys
# apikey = config.G_API_KEY
client_id = config.FS_CLIENT_ID
secret = config.FS_CLIENT_SECRET

# gets restaurants from a given location
class User(object):
    """
    User superclass. Stores basic lat / lon data for each user as a comma-separated string value
    """
    def __init__(self):
        self.location = ''

class Place(object):
    """
    Place superclass. Gets various detail attributes from the Foursquare api
    using Curl. Requires a Foursquare venue_id to construct.
    """
    def __init__(self, venue_id):
        self.venue_id = '42a0ef00f964a520cc241fe3'
        # Curl to get Foursquare Happy String
        url = ("https://api.foursquare.com/v2/venues/%s/menu?client_id=%s&client_"
               "secret=%s&v=20170109" % \
               (self.venue_id, client_id, secret)
              )
        happy_strings = ApiConnect.get_load(url)
        self.happy_string = ''
        self.has_happy_hour = False
        for menu in happy_strings.get('response').get('menu').get('menus')\
        .get('items', [{'name': '', 'description': ''}]):
            if 'happy hour' in str(menu.get('name', '')).lower() or \
            'happy hour' in str(menu.get('description', '')).lower():
                self.happy_string = menu.get('description').lower()
                self.has_happy_hour = True
                break
        # Curl to get Foursquare venue details if venue has Happy Hour
        if self.has_happy_hour:
            url = ("https://api.foursquare.com/v2/venues/%s?client_id=%s&"
                   "client_secret=%s&v=20170109" % \
                   (self.venue_id, client_id, secret)
                  )
            venue_details = ApiConnect.get_load(url).get('response').get('venue')
            self.name = venue_details.get('name', '')
            self.lat = venue_details.get('location').get('lat', 0)
            self.lng = venue_details.get('location').get('lng', 0)
            self.website = venue_details.get('url', '')
            self.price_level = venue_details.get('price').get('tier', 0)
            self.rating = venue_details.get('rating', 0.0)
            self.formatted_phone_number = venue_details.get('contact').get('formattedPhone', '')
            self.formatted_address = venue_details.get('location').get('formattedAddress', '')
        else:
            self.name = ''
            self.lat = 0
            self.lng = 0
            self.website = ''
            self.price_level = 0
            self.rating = 0
            self.formatted_phone_number = ''
            self.formatted_address = ''

        # Log to console to check returns of API calls
        print ''
        print '***************************************************************'
        print 'venue_id: %s' % self.venue_id
        print 'Has Happy Hour: %s' % self.has_happy_hour
        print 'happy_string:'
        print '---> %s' % self.happy_string
        print 'name: %s' % self.name
        print 'lat: %d' % self.lat
        print 'lng: %d' % self.lng
        print 'website: %s' % self.website
        print 'price level: %d' % self.price_level
        print 'rating: %d' % self.rating
        print 'phone: %s' % self.formatted_phone_number
        print 'address: %s' % self.formatted_address
        print '***************************************************************'

    @staticmethod
    def get_places(coords, radius='1600'):
        """
        Gets all places within a certain meter radius of a geo using FourSquare
        Args: coords - comma-separated string in the format 'lat,long'
              radius - string of meters, max 50000, def. 1600. Ex: '32000'
        Returns: list of Place object instances
        """
        nightlife_cat = '4d4b7105d754a06376d81259'
        food_cat = '4d4b7105d754a06374d81259'

        url = ("https://api.foursquare.com/v2/venues/search?intent=browse&ll="
               "%s&radius=%s&limit=50&categoryId=%s,%s&client_id=%s&client_secret=%s&v="
               "20170109" % \
               (coords, radius, nightlife_cat, food_cat, client_id, secret)
              )
        print url
        venue_dict_list = ApiConnect.get_load(url).get('response').get('venues')
        place_object_list = []
        counter = 1
        for venue in venue_dict_list:
            print counter
            counter += 1
            venue_id = venue.get('id', '0')
            place_instance = Place(venue_id)
            place_object_list.append(place_instance)
        return place_object_list

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
