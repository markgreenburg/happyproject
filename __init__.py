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
    session['lat'] = json.loads(request.args.get('lat'))
    session['lng'] = json.loads(request.args.get('lng'))
    return redirect(None)

@app.route('/display')
def display():
    """
    gets a list of places based on a 10 mile radius from user's location
    """
    # location = str(session.get('lat',0)) + ',' + str(session.get('lng', 0))
    # place_list = Place.get_places(location)
    # user = User()
    place_list = Place.get_places(session.get('lat', 0), session.get('lng', 0)\
                 , '100')
    latlng_list = []
    for place in place_list:
        latlng_list.append([place.lat, place.lng])
    return render_template(
        "display.html", apikey=g_api_key, latlng_list=latlng_list, latitude=\
        str(session.get('lat', 0)), longitude=str(session.get('lng', 0))
    )

if __name__ == "__main__":
    app.run(threaded=True)
