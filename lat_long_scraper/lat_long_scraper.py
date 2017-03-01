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
import sys
import time

reload(sys)
sys.setdefaultencoding('utf8')

# API Keys
APIKEY = config.G_API_KEY
# CODYAPIKEY = config.CODY_G_API_KEY
FS_CLIENT_ID = config.FS_CLIENT_ID
FS_SECRET = config.FS_CLIENT_SECRET

print"Started"

querycount = 0

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
        selection = conx.query(query, *args)
        conx.close()
        return selection


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
        global querycount
        if api_call.find("foursquare") == -1:
            querycount+=1
            print querycount
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


# gets restaurants from a given location
class LatLong(object):
    """
    Stores location data
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
        self.lat = str(g_place_deets.get('result').get('geometry').get('location').get('lat'))
        self.lng = str(g_place_deets.get('result').get('geometry').get('location').get('lng'))
        self.name = str(g_place_deets.get('result').get('name'))


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
        # if fs_venue_search.get('response').get('venues') is not None or len(fs_venue_search.get('response').get('venues')) != 0:
        if len(fs_venue_search.get('response').get('venues')) > 0:
            self.fs_venue_id = str(fs_venue_search.get('response'). \
                                   get('venues')[0].get('id', '0'))
            address = (fs_venue_search.get('response'). \
                       get('venues')[0].get('location').get('formattedAddress', ''))
            self.address = str(address[0])
            # else:
            #     self.fs_venue_id = '0'
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
        for menu in fs_venue_deets.get('response').get('menu').get('menus') \
                .get('items', [{'name': '', 'description': ''}]):
            if 'happy hour' in str(menu.get('name', '')).lower() or \
                            'happy hour' in str(menu.get('description', '')).lower():
                self.happy_string = menu.get('description').lower()
                self.has_happy_hour = True
                break
    @staticmethod
    def get_places(coords, radius='1609'):
        """
        Gets all places within a certain meter radius of a geo using FourSquare
        Args: coords - comma-separated string in the format 'lat,long'
              radius - string of meters, max 50000, def. 1600. Ex: '32000'
        Returns: list of Place object instances
        """
        url = (
            "https://maps.googleapis.com/maps/api/place/radarsearch/json?"
            "location=%s&radius=%s&types=restaurant&key=%s" %
            (coords, urllib.quote_plus(radius), urllib.quote_plus(APIKEY)))
        places_list = ApiConnect.get_load(url).get('results')
        for place in places_list:
            place_id = [place][0].get('place_id')
            place_instance = Place(place_id)
            if place_instance.has_happy_hour:
                sel = 'SELECT address FROM happyhour.public.happy_strings WHERE address = $1'
                selection = DbConnect.get_named_results(sel, place_instance.address)
                checker = ''
                if selection:
                    checker = str(selection[0].address)
                if place_instance.address != checker:
                    sql = ("INSERT INTO happyhour.public.happy_strings "
                           "(happy_text, venue_id, address, latitude, "
                           "longitude) VALUES ($1, $2, $3, $4, $5)")
                    print "************STORED************"
                    DbConnect.doQuery(sql, place_instance.happy_string,
                                      place_instance.fs_venue_id, place_instance.address,
                                      float(place_instance.lat),
                                      float(place_instance.lng)
                                     )
    #
    # def insert(self):
    #     # sql = "INSERT INTO happyhour.public.happy_strings(happy_text, "
    #             "venue_id, address) VALUES ($1, $2, $3)"
    #     sel='SELECT address FROM happyhour.public.happy_strings WHERE address $1'
    #     selection = DbConnect.doQuery(sel, self.address)
    #     if selection != self.address:
    #         sql = "INSERT INTO happyhour.public.happy_strings(happy_text, "
    #               "venue_id, address) VALUES ($1, $2, $3)"
    #         print "************STORED************"
    #         DbConnect.doQuery(sql, self.happy_string, self.fs_venue_id, self.address)


def scrape():
    # start at bottom right location
    # current_lat = 29.563902
    # current_lng = -95.883179
    # # end at top right location
    # lat = 29.945415
    # lng = -95.158081
    # while current_lat < lat:
    #     while current_lng < lng:
    #         loc = LatLong()
    #         loc.location = str(current_lat) + ',' + str(current_lng)
    #         print loc.location
    #         Place.get_places(loc.location, '1610')
    #         current_lng += 0.03327
    #     current_lng = -95.883179
    #     current_lat += 0.028932
    # print "*****FINISHED*****"
###################################################################################
    # houston
    # 29.763632, -95.422854
    # start at bottom right location
    current_lat = 29.763632
    current_lng = -95.422854
    # end at top right location
    lat = 29.937085
    lng = -95.274124
    global querycount
    while current_lat < lat:
        while current_lng < lng:
            if querycount >= 1000: #number of queries to 4square
                print 'pausing'
                querycount = 0
                time.sleep(1825) #delay for one hour once 5000 queries has been hit
            loc = LatLong()
            loc.location = str(current_lat) + ',' + str(current_lng)
            print loc.location
            Place.get_places(loc.location, '1610')
            current_lng += 0.016635
        current_lng = -95.672379
        current_lat += 0.014466
    print "*****FINISHED*****"

    ####Austin Scrape
    # start here!!
    # 30.254154,-97.73598

    # current_lat = 30.254154
    # current_lng = -97.73598
    # # end at top right location
    # lat = 30.593001
    # lng = -97.562842
    # global querycount
    # while current_lat < lat:
    #     while current_lng < lng:
    #         if querycount >= 1000: #number of queries to 4square
    #             print 'pausing'
    #             querycount = 0
    #             time.sleep(1825) #delay for one hour once 5000 queries has been hit
    #         loc = LatLong()
    #         loc.location = str(current_lat) + ',' + str(current_lng)
    #         print loc.location
    #         Place.get_places(loc.location, '1610')
    #         current_lng += 0.016635
    #     current_lng = -97.885695
    #     current_lat += 0.014466
    # print "*****FINISHED*****"

# calls scraper function
scrape()
