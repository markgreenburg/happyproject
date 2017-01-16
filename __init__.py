"""
Flask Documentation:     http://flask.pocoo.org/docs/
Jinja2 Documentation:    http://jinja.pocoo.org/2/documentation/
Werkzeug Documentation:  http://werkzeug.pocoo.org/documentation/
"""

import os
import sys
import json
from flask import Flask, render_template, request, redirect, url_for, session, Markup
import bcrypt
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

@app.route('/happyhour/')
def home():
    """
    Retuns homepage template with Jumbotron and search fields to enable finding
    happy hours.
    """
    return render_template('homepage.html')

@app.route('/happyhour/convert_address', methods=['GET'])
def convert_address():
    """
    Takes the address from user's search and uses the Geocoding API to convert
    it to a lat and lng value, storing those in session. Returns the map
    template with results & pins.
    """
    session['address_bool'] = 0
    if request.args.get('is_active', 'anytime') == 'now':
        session['active_only'] = True
    else:
        session['active_only'] = False
    session['radius'] = request.args.get('radius', '20')
    address_input = request.args.get('address', '')
    if address_input:
        session['address_bool'] = 1
        coords_tuple = Place.address_to_coords(request.args.get('address', \
                       ''))
        session['lat'] = coords_tuple[0]
        session['lng'] = coords_tuple[1]
        print 'session address: %s' % request.args.get('address')
        print 'lat: %s' % session['lat']
        print 'lng: %s' % session['lng']
        print 'active_only: %s' % session.get('active_only')
        print 'radius: %s' % session.get('radius')
        return redirect(url_for('display'))
    else:
        return render_template('location.html', apikey=g_api_key)

@app.route('/happyhour/location', methods=['GET'])
def location():
    """
    gets a list of places based on a 10 mile radius from user's location
    """
    session['lat'] = json.loads(request.args.get('lat'))
    session['lng'] = json.loads(request.args.get('lng'))
    return None

@app.route('/happyhour/display')
def display():
    """
    Gets a list of places based on a passed in mile radius from user's location
    Returns render of the map template / display homepage
    """
    lat = session.get('lat', 29.7604)
    lng = session.get('lng', -95.3698)
    is_active = session.get('active_only', False)
    radius = session.get('radius', '50')
    place_list = Place.get_places(lat, lng, radius, is_active)
    return render_template(
        "display.html", place_list=place_list, apikey=g_api_key, latitude=\
        lat, longitude=lng, address_input = session.get('address_bool'))

@app.route('/happyhour/details/<int:location_id>')
def show_location(location_id):
    """
    Shows the Foursquare and happyhour details for a given id from id_venue_id
    """
    location_object = Place(location_id)
    return render_template("details.html", venue=location_object)

@app.route('/happyhour/account/create', methods=["GET", "POST"])
def create_account():
    """
    Displays form to user that allows signups
    """
    return render_template('create_account.html')

@app.route('/happyhour/account/submit', methods=["POST"])
def submit_new_account():
    """
    Takes user input and creates a new account for them
    """
    

if __name__ == "__main__":
    app.run(threaded=True)
