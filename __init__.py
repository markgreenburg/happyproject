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

apikey = config.G_API_KEY
fs_client_id = config.FS_CLIENT_ID
fs_secret = config.FS_CLIENT_SECRET

@app.route('/')
def get_map():
    """
    Homepage route - shows Google Map using the user's location
    """
    print 'rendering map template...'
    return render_template('location.html', apikey=apikey)

@app.route('/_location')
def location():
    """
    gets a list of places based on a 10 mile radius from user's location
    """
    user = User()
    lat = json.loads(request.args.get('lat'))
    lng = json.loads(request.args.get('lng'))
    user.location = str(lat) + ',' + str(lng)

    return redirect(url_for('display',lat=lat, lng=lng))

@app.route('/show_place_list')
def display():
    """
    gets a list of places based on a 10 mile radius from user's location
    """
    lat=request.args['lat']
    lng=request.args['lng']
    location = str(lat) + ',' + str(lng)
    #place_list = Place.get_places(location)
    place_list = Place.get_places('29.746036,-95.350339')
    return render_template('display.html')

if __name__ == "__main__":
    app.run()
