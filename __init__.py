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
    return render_template('location.html', apikey=apikey)

@app.route('/_location',methods=['GET'])
def location():
    """
    gets a list of places based on a 10 mile radius from user's location
    """
    user = User()
    lat = json.loads(request.args.get('lat'))
    lng = json.loads(request.args.get('lng'))
    print lat
    print lng
    user.location = str(lat) + ',' + str(lng)

    return redirect(url_for('display', latlng=user.location))

@app.route('/location/<latlng>')
def display(latlng):
    """
    gets a list of places based on a 10 mile radius from user's location
    """
    # lat = request.args.get('lat')
    # lng = request.args.get('lng')

    print 'display'
    # location = str(lat) + ',' + str(lng)
    # place_list = Place.get_places(location)

    return render_template(
        "display.html",
        latlng=latlng, apikey=apikey)

if __name__ == "__main__":
    app.run()
