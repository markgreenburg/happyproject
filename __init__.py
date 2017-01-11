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
app.secret_key = 'secret'
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
    session['lat'] = json.loads(request.args.get('lat'))
    session['lng'] = json.loads(request.args.get('lng'))
    return redirect(None)

@app.route('/display')
def display():
    """
    gets a list of places based on a 10 mile radius from user's location
    """
    user = User(str(session.get('lat', 0)), str(session.get('lng', 0)))
    # user.radius = str(session.get('radius'))
    radius = '5' # string, in miles. optional arg, defaults to '1'
    place_list = Place.get_places(user.lat, user.lng, radius)
    print place_list
    latlng_list = []
    for place in place_list:
        latlng_list.append([place.lat, place.lng])
    print latlng_list
    print type(latlng_list[0][0])
    return render_template(
        "display.html", apikey=apikey, latlng_list=latlng_list, latitude=\
        user.lat, longitude=user.lng)

if __name__ == "__main__":
    app.run(threaded=True)
