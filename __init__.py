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

lat = 0
lng = 0
@app.route('/happyhour/')
def home():
    """
    Homepage route - shows Google Map using the user's location
    """
    return render_template('homepage.html')

@app.route('/happyhour/getlocation')
def get_map():
    """
    Homepage route - shows Google Map using the user's location
    """
    return render_template('location.html', apikey=g_api_key)

@app.route('/happyhour/location', methods=['GET'])
def location():
    """
    gets a list of places based on a 10 mile radius from user's location
    """
    global lat
    global lng
    lat = json.loads(request.args.get('lat'))
    lng = json.loads(request.args.get('lng'))
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

    global lat
    global lng
    place_list = Place.get_places(lat, lng, '50', False)
    # latlng_list = []
    # place_list = place_list
    # place_list_length = len(place_list)
    # for place in place_list:
    #     # place_form_add = str(place.formatted_address[0])
    #     place_name = str(place.name)
    #     latlng_list.append([float(place.lat), float(place.lng), place_name])
    return render_template(
        "display.html", place_list=place_list, apikey=g_api_key, latitude=\
        lat, longitude=lng)

@app.route('/happyhour/details/<int:location_id>')
def show_location(location_id):
    """
    Shows the Foursquare and happyhour details for a given id from id_venue_id
    """
    location_object = Place(location_id)
    return render_template("details.html", venue=location_object)

if __name__ == "__main__":
    app.run(threaded=True)
