"""
Fetches venue from Google Places and Foursquare APIs
"""

import sys
import time
import urllib
import config
from .. import models

# API Keys
APIKEY = config.G_API_KEY
FS_CLIENT_ID = config.FS_CLIENT_ID
FS_SECRET = config.FS_CLIENT_SECRET

reload(sys)
sys.setdefaultencoding('utf8')

class Place(object):
    """
    Place scraper class. Gets various detail attributes from the Foursquare api
    using Curl. Requires a Foursquare venue_id to construct.
    """
    def __init__(self, place_id):
        self.place_id = place_id
        # Curl to get place details from Google
        url = "https://maps.googleapis.com/maps/api/place/details/json?placeid=%s&key=%s" % (
            urllib.quote_plus(self.place_id), urllib.quote_plus(APIKEY))
        g_place_deets = models.ApiConnect.get_load(url)
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
        fs_venue_search = models.ApiConnect.get_load(url)
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
        fs_venue_deets = models.ApiConnect.get_load(url)

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
        places_list = models.ApiConnect.get_load(url).get('results')
        for place in places_list:
            place_id = [place][0].get('place_id')
            place_instance = Place(place_id)
            if place_instance.has_happy_hour:
                sel = 'SELECT address FROM happyhour.public.happy_strings WHERE address = $1'
                selection = models.DbConnect.get_named_results(sel, False, place_instance.address)
                checker = ''
                if selection:
                    checker = str(selection[0].address)
                if place_instance.address != checker:
                    sql = ("INSERT INTO happyhour.public.happy_strings "
                           "(happy_text, venue_id, address, latitude, "
                           "longitude) VALUES ($1, $2, $3, $4, $5)")
                    print "************STORED************"
                    models.DbConnect.doQuery(sql, place_instance.happy_string,
                                             place_instance.fs_venue_id,
                                             place_instance.address,
                                             float(place_instance.lat),
                                             float(place_instance.lng)
                                            )

def scrape(start_lat, start_lng, end_lat, end_lng):
    """
    Scrapes foursquare within a given lat / lng rectangle. Writes results
    to db.
    """
    print "Scraper started"
    current_lat = start_lat
    current_lng = start_lng
    querycount = 0
    while current_lng < end_lng:
        while current_lat < end_lat:
            if querycount > 1000:
                print "Querylimit reached. Pausing..."
                querycount = 0
                time.sleep(1825) # one hour
            coords = str(current_lat) + "," + str(current_lng)
            Place.get_places(coords, '1610')
            current_lat += 0.0145
            querycount += 1
        current_lat = start_lat
        current_lng += 0.0145
    print "Done fetching results"


