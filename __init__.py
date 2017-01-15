"""
Flask Documentation:     http://flask.pocoo.org/docs/
Jinja2 Documentation:    http://jinja.pocoo.org/2/documentation/
Werkzeug Documentation:  http://werkzeug.pocoo.org/documentation/
"""

import os
import sys
import json
from flask import Flask, render_template, request, redirect, url_for, session, Markup
import requests
from models import *
import config

reload(sys)
sys.setdefaultencoding('utf8')
app = Flask(__name__)
g_api_key = config.G_API_KEY
fs_client_id = config.FS_CLIENT_ID
fs_secret = config.FS_CLIENT_SECRET
app.config['SECRET_KEY'] = config.SECRET_KEY
app.config['APPLICATION_ROOT'] = config.APPLICATION_ROOT
app.config['DEBUG'] = config.DEBUG

# lat = 0
# lng = 0
@app.route('/happyhour/')
def home():
    """
    Retuns homepage template with Jumbotron and search fields to enable finding
    happy hours.
    """
    return render_template('homepage.html')

@app.route('/convert_address', methods=['GET'])
def convert_address():
    """
    Takes the address from user's search and uses the Geocoding API to convert
    it to a lat and lng value, storing those in session. Returns the map
    template with results & pins.
    """
    session['address_input'] = 0
    if request.args.get('is_active', 'anytime') == 'now':
        session['active_only'] = True
    else:
        session['active_only'] = False
    session['radius'] = request.args.get('radius', '20')
    address_input = request.args.get('address', '')
    if address_input:
        coords_tuple = Place.address_to_coords(request.args.get('address', \
                       ''))
        session['lat'] = coords_tuple[0]
        session['lng'] = coords_tuple[1]
        session['address_input'] = 1
        print 'session address: %s' % request.args.get('address')
        print 'lat: %s' % session['lat']
        print 'lng: %s' % session['lng']
        print 'active_only: %s' % session.get('active_only')
        print 'radius: %s' % session.get('radius')
        return redirect(url_for('display'))
    else:
        return render_template('location.html', apikey=g_api_key)

@app.route('/happyhour/getlocation')
def get_map():
    """
    Template for getting user's location automatically. Page uses HTML5
    geolocation to get user's lat / lng, then redirects user to the map page
    with a JS redirect.
    """
    return render_template('location.html', apikey=g_api_key)

@app.route('/happyhour/location', methods=['GET'])
def location():
    """
    gets a list of places based on a 10 mile radius from user's location
    """
    # Mark commented out the next four lines and added the following three
    # global lat
    # global lng
    # lat = json.loads(request.args.get('lat'))
    # lng = json.loads(request.args.get('lng'))
    session['lat'] = json.loads(request.args.get('lat'))
    session['lng'] = json.loads(request.args.get('lng'))
    return redirect(None)

@app.route('/happyhour/display')
def display():
    """
    Gets a list of places based on a passed in mile radius from user's location
    Returns render of the map template / display homepage
    """
    # location = str(session.get('lat',0)) + ',' + str(session.get('lng', 0))
    # place_list = Place.get_places(location)
    # user = User()

    #todo create radius dropdown in homepage and tickbox for all happy hours or current
    #todo get input from submit button if true call with models.apiconnect, if false return false.
    #todo set lat/lng to geocoding if true
    # Mark commented out the next two lines
    # global lat
    # global lng
    # Mark commented out the next line and replaced it with the following four lines
    # place_list = Place.get_places(lat, lng, '50', False)
    lat = session.get('lat', 29.7604)
    lng = session.get('lng', -95.3698)
    is_active = session.get('active_only', False)
    radius = session.get('radius', '50')
    # print 'search settings:'
    # print 'lat: %f' % lat
    # print 'lng: %f' % lng
    # print 'is_active %s' % is_active
    # print 'radius: %s' % radius
    place_list = Place.get_places(lat, lng, radius, is_active)
    # latlng_list = []
    # place_list = place_list
    # place_list_length = len(place_list)
    # for place in place_list:
    #     # place_form_add = str(place.formatted_address[0])
    #     place_name = str(place.name)
    #     latlng_list.append([float(place.lat), float(place.lng), place_name])
    return render_template(
        "display.html", place_list=place_list, apikey=g_api_key, latitude=\
        lat, longitude=lng, address_input = session.get('address_input'))

@app.route('/happyhour/details/<int:location_id>')
def show_location(location_id):
    """
    Shows the Foursquare and happyhour details for a given id from id_venue_id
    """
    location_object = Place(location_id)
    return render_template("details.html", venue=location_object)

if __name__ == "__main__":
    app.run(threaded=True)
