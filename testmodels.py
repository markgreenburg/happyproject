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
        print url
        fs_venue_search = ApiConnect.get_load(url)
        print fs_venue_search
        if len(fs_venue_search.get('response').get('venues')) > 0:
            self.fs_venue_id = str(fs_venue_search.get('response'). \
                                   get('venues')[0].get('id', '0'))
            print self.fs_venue_id
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
        for menu in fs_venue_deets.get('response').get('menu').get('menus') \
                .get('items', [{'name': '', 'description': ''}]):
            if 'happy hour' in str(menu.get('name', '')).lower() or \
                            'happy hour' in str(menu.get('description', '')).lower():
                self.happy_string = menu.get('description').lower()
                print 'name: %s' % self.name
                print 'happy_string:'
                print '---> %s' % self.happy_string
                break

    @staticmethod
    def get_places(coords, radius='30000'):
        """
        Gets all places within a certain meter radius of a geo using FourSquare
        Args: coords - comma-separated string in the format 'lat,long'
              radius - string of meters, max 50000, def. 1600. Ex: '32000'
        Returns: list of Place object instances
        """
        url = (
            "https://maps.googleapis.com/maps/api/place/radarsearch/json?location=%s&radius=%s&types=restaurant&key=%s" %
            (coords, urllib.quote_plus(radius), urllib.quote_plus(APIKEY)))
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
