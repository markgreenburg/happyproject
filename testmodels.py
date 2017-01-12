###GET DATA

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
    Place superclass. Gets various detail attributes from the Foursquare api
    using Curl. Requires a Foursquare venue_id to construct.
    """

    def __init__(self, place_id):
        self.place_id = place_id
        # Curl to get place details from Google
        url = "https://maps.googleapis.com/maps/api/place/details/json?placeid=%s&key=%s" % (
            urllib.quote_plus(self.place_id), urllib.quote_plus(APIKEY))
        g_place_deets = ApiConnect.get_load(url)
        self.lat = str(g_place_deets.get('result', {}).get('geometry', {}).get('location', {}).get('lat', {}))
        self.lng = str(g_place_deets.get('result', {}).get('geometry', {}).get('location', {}).get('lng', {}))
        self.name = str(g_place_deets.get('result', {}).get('name', {}))

        # Curl to get Foursquare venue ID
        url = ("https://api.foursquare.com/v2/venues/search?intent=match&ll=%s"
               "&query=%s&client_id=%s&client_secret=%s&v=20170109" %
               ((str(self.lat + ',' + self.lng)),
                urllib.quote_plus(self.name),
                urllib.quote_plus(FS_CLIENT_ID),
                urllib.quote_plus(FS_SECRET)
                )
               )
        fs_venue_search = ApiConnect.get_load(url)
        if len(fs_venue_search.get('response', {}).get('venues', {})) > 0:
            self.fs_venue_id = str(fs_venue_search.get('response', {}). \
                                   get('venues', {})[0].get('id', '0'))
            address = (fs_venue_search.get('response'). \
                                   get('venues', {})[0].get('location', {}).get('formattedAddress', ''))
            self.address = str(address[0])
            print'************'
            print'************'
            print self.address
            print self.fs_venue_id
            print'************'
            print'************'
        else:
            self.fs_venue_id = '0'
        # Curl to get Foursquare happy hour menu description
        url = ("https://api.foursquare.com/v2/venues/%s/menu?client_id=%s&client_"
               "secret=%s&v=20170109" %
               (urllib.quote_plus(self.fs_venue_id),
                urllib.quote_plus(FS_CLIENT_ID),
                urllib.quote_plus(FS_SECRET)
                )
               )
        fs_venue_deets = ApiConnect.get_load(url)

        self.happy_string = ''
        self.has_happy_hour = False
        for menu in fs_venue_deets.get('response', {}).get('menu', {}).get('menus', {}) \
                .get('items', [{'name': '', 'description': ''}]):
            if 'happy hour' in str(menu.get('name', '')).lower() or \
                            'happy hour' in str(menu.get('description', '')).lower():
                self.happy_string = menu.get('description', {}).lower()
                self.has_happy_hour = True
                break
        # Curl to get Foursquare venue details if venue has Happy Hour
        # if self.has_happy_hour:
            # url = ("https://api.foursquare.com/v2/venues/%s?client_id=%s&"
            #        "client_secret=%s&v=20170109" % \
            #        (self.fs_venue_id, FS_CLIENT_ID, FS_SECRET)
            #        )
            # venue_details = ApiConnect.get_load(url).get('response').get('venue')
            # self.name = venue_details.get('name', '')
            # self.lat = venue_details.get('location').get('lat', 0)
            # self.lng = venue_details.get('location').get('lng', 0)
            # self.website = venue_details.get('url', '')
            # self.price_level = venue_details.get('price').get('tier', 0)
            # self.rating = venue_details.get('rating', 0.0)
            # self.formatted_phone_number = venue_details.get('contact').get('formattedPhone', '')
            # self.formatted_address = venue_details.get('location').get('formattedAddress', '')

    @staticmethod
    def get_places(coords, radius='1609'):
        """
        Gets all places within a certain meter radius of a geo using FourSquare
        Args: coords - comma-separated string in the format 'lat,long'
              radius - string of meters, max 50000, def. 1600. Ex: '32000'
        Returns: list of Place object instances
        """
        url = (
            "https://maps.googleapis.com/maps/api/place/radarsearch/json?location=%s&radius=%s&types=restaurant&key=%s" %
            (coords, urllib.quote_plus(radius), urllib.quote_plus(APIKEY)))
        places_list = ApiConnect.get_load(url).get('results', {})
        place_objects_list = []
        for place in places_list:
            place_id = [place][0].get('place_id', {})
            place_instance = Place(place_id)
            print place_instance.address
            if place_instance.has_happy_hour:
                ven_id = 'SELECT venue_id FROM happyhour.public.happy_strings WHERE venue_id = $1'
                venue_id_exists = DbConnect.get_named_results(ven_id, place_instance.fs_venue_id)
                ven_add = 'SELECT address FROM happyhour.public.happy_strings WHERE venue_id = $1'
                venue_add_exists = DbConnect.get_named_results(ven_add, place_instance.fs_venue_id)
                if venue_id_exists != place_instance.fs_venue_id and venue_add_exists != place_instance.address:
                    place_instance.insert()

    def insert(self):
        sql = 'INSERT INTO happyhour.public.happy_strings(happy_text, venue_id, address) VALUES ($1, $2, $3)'

        DbConnect.doQuery(sql, self.happy_string, self.fs_venue_id, self.address)


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
    def get_named_results(sql, *args):
        """
        Opens a connection to the db, executes a query, gets results using
        pSQL's named_results, and then closes the connection.
        Args: query - pSQL query as string
              *args - pass in as many parameters for the query as needed
        Returns: the fetchOne or fetchAll of the query
        """
        conx = DbConnect.get_connection()
        query = conx.query(sql, *args)
        print query
        result_list = query.namedresult()
        conx.close()
        return result_list

    @staticmethod
    def doQuery(query, *args):
        """
        Opens a connection to the db, executes a query, gets results using
        pSQL's named_results, and then closes the connection.
        Args: query - pSQL query as string
              *args - pass in as many parameters for the query as needed
        Returns: the fetchOne or fetchAll of the query
        """
        conx = DbConnect.get_connection()
        query = conx.query(query, *args)
        print query
        conx.close()


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
