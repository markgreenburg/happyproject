"""
Module holds the object models, API calls, and db connections for the Happy
Hour app
"""
import datetime
import json
import StringIO
import urllib
import pycurl
import bcrypt
import config
import pg

# API Keys: Google
apikey = config.G_API_KEY
# API Keys: FS
client_id = config.FS_CLIENT_ID
secret = config.FS_CLIENT_SECRET

class User(object):
    """
    User class. Stores basic lat / lon data for each user as a
    comma-separated string value. Will add auth, add / edit
    functionality as fast-follow.
    """
    def __init__(self, lat='', lng=''):
        self.firstname = ''

    @staticmethod
    def check_unique(username):
        """
        Checks whether a user's given username already exists in the system.
        Args: username - A string of the user's chosen username
        Returns: Bool - True if name unique or False if already in db
        """
        query = ("SELECT id FROM happyhour.public.users WHERE username"
                 " = $1 LIMIT 1")
        user_matches = DbConnect.get_named_results(query, True, username)
        if len(user_matches) > 0:
            return False
        return True



class Place(object):
    """
    Place superclass. Gets various detail attributes from the Foursquare api
    using Curl. Generates based on internal ID for each venue.
    """
    def __init__(self, location_id=0):
        # Get local info from our db
        sql = ("SELECT venues.id, venue_id, lat, lng FROM"
               " happyhour.public.id_venue_id venues INNER JOIN"
               " happyhour.public.coordinates coords ON venues.id ="
               " coords.location_id WHERE venues.id = $1 LIMIT 1"
              )
        venue_db_object = DbConnect.get_named_results(sql, True, location_id)
        if venue_db_object:
            self.location_id = venue_db_object.id
            self.venue_id = venue_db_object.venue_id
            self.lat = venue_db_object.lat
            self.lng = venue_db_object.lng
            self.happy_hour = Day.get_days(self.location_id)
            # Curl to get Foursquare venue details
            url = ("https://api.foursquare.com/v2/venues/%s?client_id=%s&"
                   "client_secret=%s&v=20170109" % \
                   (self.venue_id, \
                    client_id, \
                    secret)
                  )
            self.is_happy_hour = self.get_happy_state()
            venue_details = ApiConnect.get_load(url).get('response', {}).get\
                            ('venue', {})
            self.name = venue_details.get('name', '')
            self.description = venue_details.get('page', {}).get('pageInfo', \
                               {}).get('description', '')
            self.website = venue_details.get('url', '')
            self.img_prefix = venue_details.get('bestPhoto', {}).get('prefix'\
                              , '')
            self.img_suffix = venue_details.get('bestPhoto', {}).get('suffix'\
                              , '')
            self.img_width = venue_details.get('bestPhoto', {}).get\
                               ('width', 0)
            self.img_height = venue_details.get('bestPhoto', {}).get('height'\
                               , 0)
            self.category = venue_details.get('categories', [{}])[0].get \
                              ('name', '')
            self.specials = venue_details.get('specials', {}).get('items', [{}])
            self.tips = self.get_tips(venue_details)
            self.menu_url = venue_details.get('menu', {}).get('url', '')
            self.hours_today = venue_details.get('hours', {}).get('status', '')
            self.is_open = venue_details.get('hours', {}).get('isOpen', False)
            self.price_level = venue_details.get('price', {}).get('tier', 0)
            self.rating = venue_details.get('rating', 0.0)
            self.formatted_phone_number = venue_details.get('contact', {}).get\
            ('formattedPhone', '')
            self.formatted_address = venue_details.get('location', {}).get\
            ('formattedAddress', [])
        else:
            self.location_id = 0
            self.venue_id = ''
            self.lat = 0
            self.lng = 0
            self.happy_hour = [{}]
            self.is_happy_hour = False
            self.name = ''
            self.description = ''
            self.website = ''
            self.img_prefix = ''
            self.img_suffix = ''
            self.img_width = 0
            self.img_height = 0
            self.category = ''
            self.specials = [{}]
            self.tips = [{}]
            self.menu_url = ''
            self.hours_today = ''
            self.is_open = False
            self.price_level = 0
            self.rating = 0.0
            self.formatted_phone_number = ''
            self.formatted_address = [{}]
        # Log to console to check returns of API calls
        print ''
        print '***************************************************************'
        print 'name: %s' % self.name
        print 'location_id: %d' % self.location_id
        print 'venue_id: %s' % self.venue_id
        print 'lat: %f' % self.lat
        print 'lng: %f' % self.lng
        print 'website: %s' % self.website
        print 'full image link: %s' % self.img_prefix + '500x500' + \
              self.img_suffix
        print 'image dimensions: %s' % str(self.img_width) + 'x' + \
              str(self.img_height)
        print 'main category: %s' % self.category
        print 'menu url: %s' % self.menu_url
        print 'hours_today: %s' % self.hours_today
        print 'is_open: %s' % self.is_open
        print 'price level: %d' % self.price_level
        print 'rating: %d' % self.rating
        print 'phone: %s' % self.formatted_phone_number
        print 'address: %s' % self.formatted_address
        print 'specials: %s' % self.specials
        print 'tips: %s' % self.tips
        print 'is_happy_hour: %s' % self.is_happy_hour
        print 'Happy Hour Times: %s' % self.happy_hour
        print '***************************************************************'

    def get_happy_state(self):
        """
        Determines whether happy hour is currently open using self.happy_hour
        object list. Returns True if happy hour is currently open or False.
        """
        # Our week starts on Monday = 1, Python's Monday = 0
        today = datetime.datetime.today().weekday() + 1
        now = datetime.datetime.now().time()
        for day in self.happy_hour:
            if now > day.end_time \
            and now < day.start_time \
            and today == day.day_of_week:
                return True
        return False

    def insert(self):
        """
        Inserts new venue records into our database.
        Is called by the save() method
        """
        # Insert into venues & coords tables
        sql = ("WITH venues AS (INSERT INTO happyhour.public.id_venue_id"
               " (venue_id) VALUES ($1) RETURNING id) INSERT INTO"
               " happyhour.pulic.coordinates (location_id, lat, lng) SELECT id,"
               " $2, $3 FROM venues RETURNING id"
              )
        result_obj = DbConnect.get_named_results(sql, True, self.venue_id, \
                     self.lat, self.lng)
        self.location_id = result_obj.id
        return self.location_id

    def update(self):
        """
        Updates an existing Place record. Is called by the save() method.
        """
        sql = ("WITH updated_venue AS (UPDATE happyhour.pulic.id_venue_id SET"
               " venue_id = $1 WHERE id = $2 RETURNING id) UPDATE"
               " happyhour.public.coordinates SET lat = $3, lng = $4 WHERE"
               " location_id IN (SELECT id from updated_venue) RETURNING"
               " location_id;"
              )
        result_obj = DbConnect.get_named_results(sql, True, self.venue_id,\
                     self.location_id, self.lat, self.lng)
        return result_obj.location_id

    def save(self):
        """
        Saves to database, using either insert() or update() methods depending
        on whether or not result already exists in our database
        Args: self - uses self.location_id to determine whether to call insert()
                     or update()
        Returns: self.location_id
        """
        if self.location_id > 0:
            self.update()
        else:
            self.insert()
        return self.location_id

    def set_delete(self, deleted=True):
        """
        Sets deleted property in id_venue_id table.
        Args: deleted - Optional Bool type, defaults to True
        Returns: id from the updated row in id_venue_id
        """
        sql = ("UPDATE happyhour.public.id_venue_id SET deleted = $1 WHERE"
               " id = $2")
        result_obj = DbConnect.get_named_results(sql, True, deleted, \
                     self.location_id)
        return result_obj.location_id

    @staticmethod
    def get_places(lat, lng, radius='1', active_only=False):
        """
        Gets all places within a certain mile radius of a geo from DB
        Args: lat - comma-separated string of a float lat, e.g. '-29.67'
              lng - comma-separated string of a float lng, e.g. '95.43'
              radius(opt) - string of miles, min '1', default '1'
              is_active(opt) - Bool, restricts results to only those that
                               are active now
        Returns: list of Place object instances
        """
        # For more info on the below query, see:
        # http://www.movable-type.co.uk/scripts/latlong.html
        # Get all results within specified radius, order results by distance
        sql = ("SELECT location_id, (acos(sin(lat * 0.0175) * sin($1 * 0.0175)"
               " + cos(lat * 0.0175) * cos($2 * 0.0175) * cos(($3 * 0.0175) -"
               " (lng * 0.0175))) * 3959) as milesfromuser FROM"
               " happyhour.public.coordinates WHERE (acos(sin(lat * 0.0175) *"
               " sin($4 * 0.0175) + cos(lat * 0.0175) * cos($5 * 0.0175) *"
               " cos(($6 * 0.0175) - (lng * 0.0175))) * 3959 <= $7) ORDER BY"
               " milesfromuser ASC;"
              )
        venue_id_objects = DbConnect.get_named_results(sql, False, lat, lat, \
                           lng, lat, lat, lng, radius)
        place_object_list = []
        for venue_row in venue_id_objects:
            place_instance = Place(venue_row[0])
            if active_only and place_instance.is_happy_hour:
                place_object_list.append(place_instance)
            elif not active_only:
                place_object_list.append(place_instance)
        return place_object_list

    @staticmethod
    def get_tips(fs_api_object):
        """
        Extracts all tips of type 'others' from the object returned by the fs
        api. Returns a list of objects containing tip text and user firstname
        """
        tips_obj = fs_api_object.get('tips', {}).get('groups', [{}])
        others_tip_obj = {}
        for tip_group in tips_obj:
            if tip_group.get('type') == 'others':
                others_tip_obj = tip_group
                break
        tip_info_list = []
        for item in others_tip_obj.get('items', [{}]):
            tip_text = item.get('text', '')
            tip_user = item.get('user', {}).get('firstName', '')
            tip_dict = {'name': tip_user, 'text': tip_text}
            tip_info_list.append(tip_dict)
        return tip_info_list

    @staticmethod
    def address_to_coords(address):
        """
        Converts address strings to lat and lng coordinates
        Args: address - In string format, e.g., '1600 amphitheatre parkway'
        Returns: (lat, lng) - A tuple of the location's coordinates
        """
        url = ("https://maps.googleapis.com/maps/api/geocode/json?address=%s"
               "&key=%s" % (urllib.quote_plus(address), apikey)
              )
        location_data = ApiConnect.get_load(url)
        lat = location_data.get('results', [{}])[0].get('geometry', {}).\
              get('location', {}).get('lat', 0)
        lng = location_data.get('results', [{}])[0].get('geometry', {}).\
              get('location', {}).get('lng', 0)
        return (lat, lng)


class Day(object):
    """
    Defines an individual day on which a Place has a Happy Hour.
    """
    def __init__(self, day_time_id=0, day_of_week=0, loc_id=0):
        if day_time_id > 0:
            sql = ("SELECT id, location_id, day_of_week, start_time, end_time"
                   " FROM happyhour.public.id_times WHERE id = $1")
            day_info = DbConnect.get_named_results(sql, True, day_time_id)
        elif day_of_week > 0 and loc_id > 0:
            sql = ("SELECT id, location_id, day_of_week, start_time, end_time"
                   " FROM happyhour.pulic.id_times WHERE day_of_week = $1 AND"
                   " location_id = $2")
            day_info = DbConnect.get_named_results(sql, True, day_of_week, \
                       loc_id)
        if day_info:
            self.day_time_id = day_info.id
            self.location_id = day_info.location_id
            self.day_of_week = day_info.day_of_week
            self.day_string = self.get_day_string()
            self.start_time = day_info.start_time
            self.end_time = day_info.end_time
        else:
            self.day_of_week = 0
            self.day_string = ''
            self.location_id = 0
            self.day_time_id = day_time_id
            self.start_time = '00:00:00'
            self.end_time = '00:00:00'

    def get_day_string(self):
        """
        Gives us a human-readable version of the day
        """
        if self.day_of_week == 1:
            day_string = 'Monday'
        elif self.day_of_week == 2:
            day_string = 'Tuesday'
        elif self.day_of_week == 3:
            day_string = 'Wednesday'
        elif self.day_of_week == 4:
            day_string = 'Thursday'
        elif self.day_of_week == 5:
            day_string = 'Friday'
        elif self.day_of_week == 6:
            day_string = 'Saturday'
        elif self.day_of_week == 7:
            day_string = 'Sunday'
        # make sure we set day_string to something if no matchces
        else:
            day_string = ''
        return day_string

    def insert(self):
        """
        Inserts a new day-of-week record into the id_times table. Returns
        the id of the new insert.
        """
        sql = ("INSERT INTO happyhour.public.id_times (location_id,"
               " day_of_week, start_time, end_time) VALUES ($1, $2, $3, $4)"
               " RETURNING id"
              )
        result_obj = DbConnect.get_named_results(sql, True, self.location_id, \
                     self.day_of_week, self.start_time, self.end_time)
        self.day_time_id = result_obj.id
        return self.day_time_id

    def update(self):
        """
        Updates existing day record in id_times table.
        Returns: record's id.
        """
        sql = ("UPDATE happyhour.pulic.id_times SET location_id = $1,"
               " day_of_week = $2, start_time = $3, end_time = $4 WHERE"
               " id = $5 RETURNING id"
              )
        result_obj = DbConnect.get_named_results(sql, True, self.location_id, \
                     self.day_of_week, self.start_time, self.end_time, \
                     self.day_time_id)
        return result_obj.id

    def save(self):
        """
        Saves day record into db using either update() or insert() depending on
        instance properties location_id and day_of_week
        Returns: the internal id of the record in the id_times table
        """
        if self.location_id > 0 and self.day_of_week > 0:
            self.update()
        else:
            self.insert()
        return self.day_time_id

    def set_delete(self, deleted=True):
        """
        Sets deleted property for each record in the id_times table.
        Args: deleted - optional Bool, defaults to True.
        Returns: the internal id of the updated object.
        """
        sql = ("UPDATE happyhour.public.id_times SET deleted = $1 WHERE"
               " id = $2")
        result_obj = DbConnect.get_named_results(sql, True, deleted, \
                     self.day_time_id)
        return result_obj.id

    @staticmethod
    def get_days(location_id):
        """
        Gets a list of day objects based for each location_id in asc order
        """
        sql = ("SELECT id FROM happyhour.public.id_times WHERE location_id"
               " = $1 ORDER BY day_of_week ASC"
              )
        day_id_list = DbConnect.get_named_results(sql, False, location_id)
        day_objects_list = []
        for day in day_id_list:
            day_object = Day(day[0])
            day_objects_list.append(day_object)
        return day_objects_list

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
        curl_object = pycurl.Curl()
        curl_object.setopt(curl_object.URL, api_call)
        curl_object.setopt(curl_object.WRITEFUNCTION, response.write)
        curl_object.setopt(curl_object.HTTPHEADER, ['Content-Type: application/json', \
        'Accept-Charset: UTF-8'])
        curl_object.perform()
        curl_object.close()
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
        Sets up the postgreSQL connection by loading in db settings from config
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
        if get_one:
            results = results[0]
        conx.close()
        return results
