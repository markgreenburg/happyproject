"""
Flask Documentation:     http://flask.pocoo.org/docs/
Jinja2 Documentation:    http://jinja.pocoo.org/2/documentation/
Werkzeug Documentation:  http://werkzeug.pocoo.org/documentation/

"""
import os
import sys
from flask import Flask, render_template, request, redirect, url_for, session, Markup
import user
import config

reload(sys)
sys.setdefaultencoding('utf8')

app = Flask(__name__)

@app.route('/')
def get_map():
    """
    Renders Google Maps template with user's location.
    """
    # user = User()
    return render_template('location.html', apikey=config.apikey)

if __name__ == "__main__":
    app.run()
