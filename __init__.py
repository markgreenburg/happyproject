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
@app.route('/')
def get_map():
    """
    Homepage route - shows Google Map using the user's location
    """
    return render_template('location.html', apikey=g_api_key)

@app.route('/_location', methods=['GET'])
def location():
    """
    gets a list of places based on a 10 mile radius from user's location
    """
    global lat
    global lng
    lat = json.loads(request.args.get('lat'))
    lng = json.loads(request.args.get('lng'))
    return redirect(None)

@app.route('/display')
def display():
    """
    gets a list of places based on a 10 mile radius from user's location
    """
    # location = str(session.get('lat',0)) + ',' + str(session.get('lng', 0))
    # place_list = Place.get_places(location)
    # user = User()

    global lat
    global lng
    place_list = Place.get_places(lat, lng\
                 , '100')
    latlng_list = []
    place_list = place_list
    place_list_length = len(place_list)
    for place in place_list:
        latlng_list.append([float(place.lat), float(place.lng)])
    for place in place_list:
        for day in place.happy_hour:
            print'###################'
            print day.day_of_week
            print day.start_time
            print day.end_time
            print'###################'
    return render_template(
        "display.html", place_list=place_list, place_list_length=place_list_length, apikey=g_api_key, latlng_list=latlng_list, latitude=\
        lat, longitude=lng)

@app.route('/details/<int:location_id>')
def show_location(location_id):
    """
    Shows the Foursquare and happyhour details for a given id from id_venue_id
    """
    venue = Place(location_id)
    return render_template("details.html", location_object=venue)

if __name__ == "__main__":
    app.run(threaded=True)
