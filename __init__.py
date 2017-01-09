"""
Flask Documentation:     http://flask.pocoo.org/docs/
Jinja2 Documentation:    http://jinja.pocoo.org/2/documentation/
Werkzeug Documentation:  http://werkzeug.pocoo.org/documentation/

"""
import os
from flask import Flask, render_template, request, redirect, url_for, session, Markup
import sys
from user import *
import json
import requests

reload(sys)
sys.setdefaultencoding('utf8')

app = Flask(__name__)

@app.route('/')
def getMap():
    return render_template('location.html', apikey = config.apikey)

@app.route('/_location')
def location():
    user = User()
    lat = json.loads(request.args.get('lat'))
    lng = json.loads(request.args.get('lng'))
    # do some stuff
    user.loc = {'latitude':lat, 'longitude':lng}
    user.getURL(user.loc)
    return render_template('location.html', apikey=config.apikey)


    # response = request.get_json('loc')
    # loc = json.loads(response.text)
    # # do some stuff
    # print (loc[0])



if __name__ == "__main__":
    app.run()
