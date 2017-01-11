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
    User superclass. Stores basic lat / lon data for each user as a
    comma-separated string value
    """
    def __init__(self, lat='', lng=''):
        self.lat = lat
        self.lng = lng

class Place(object):
    """
    Place superclass. Gets various detail attributes from the Foursquare api
    using Curl. Generates based on internal ID for each venue.
    """
    def __init__(self, location_id):
        self.location_id = location_id
        # Get FS venue_id from database
        sql = "SELECT venue_id FROM happyhour.public.id_venue_id WHERE id = $1 LIMIT 1"
        self.venue_id = DbConnect.get_named_results(sql, True, self.location_id).venue_id
        # Curl to get Foursquare Happy String
        url = ("https://api.foursquare.com/v2/venues/%s/menu?client_id=%s&client_"
               "secret=%s&v=20170109" % \
               (self.venue_id, client_id, secret)
              )
        print url
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

    def save(self):
        """
        Saves to database, using either insert() or update() methods depending
        on whether or not result already exists in our database
        """

    @staticmethod
    def get_places(lat, lng, radius='1'):
        """
        Gets all places within a certain mile radius of a geo from DB
        Args: lat - comma-separated string of a float lat, e.g. '-29.67'
              lng - comma-separated string of a float lng, e.g. '95.43'
              radius(opt) - string of miles, min '1', default '1'
        Returns: list of Place object instances
        """
        # For more info on the below query, see:
        # http://www.movable-type.co.uk/scripts/latlong.html
        # sql = ("SELECT id FROM happyhour.public.id_venue_id venues INNER JOIN"
        #        " happyhour.public.coordinates coords ON venues.id ="
        #        " coords.location_id WHERE (acos(sin(coords.lat * 0.0175) *"
        #        " sin($1 * 0.0175) + cos(coords.lat * 0.0175) * cos($2 *"
        #        " 0.0175) * cos(($3 * 0.0175) - (coords.lng * 0.0175))) *"
        #        " 3959 <= $4);"
        #       )
        # venue_id_objects = DbConnect.get_named_results(sql, lat, lat, lng, radius)
        sql = ("SELECT location_id FROM happyhour.public.coordinates WHERE"
               " (acos(sin(lat * 0.0175) * sin($1 * 0.0175) + cos(lat *"
               " 0.0175) * cos($2 * 0.0175) * cos(($3 * 0.0175) - (lng *"
               " 0.0175))) * 3959 <= $4);"
              )
        venue_id_objects = DbConnect.get_named_results(sql, False, lat, lat, lng, radius)
        place_object_list = []
        for venue_row in venue_id_objects:
            place_instance = Place(venue_row[0])
            place_object_list.append(place_instance)
        return place_object_list

class ApiConnect(object):
    """
    Holds Curl code to get info from our API partners
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

class DbConnect(object):
    """
    Collection of static methods that set up our DB connection and create
    generalized methods for running queries / establish and release
    connections in pSQL
    """
    @staticmethod
    def get_connection():
        """
        Sets up the postgreSQL connection by loading in params from config
        """
        return pg.DB(
            host=config.DBHOST,
            user=config.DBUSER,
            passwd=config.DBPASS,
            dbname=config.DBNAME
            )

    @staticmethod
    def escape(value):
        """
        Escapes apostrophes in SQL
        """
        return value.replace("'", "''")

    @staticmethod
    def get_named_results(sql, get_one, *args):
        """
        Opens a connection to the db, executes a query, gets results using
        pSQL's named_results, and then closes the connection.
        Args: query   - pSQL query as string
              get_one - Bool that determines whether list or first
                        result of list are returned (default = False)
              *args   - pass in as many parameters for the query as needed
        Returns: the fetchOne or fetchAll of the query
        """
        conx = DbConnect.get_connection()
        query = conx.query(sql, *args)
        results = query.namedresult()
        if len(results) == 0:
            results[0] = {}
        if get_one:
            results = results[0]
        conx.close()
        return results
