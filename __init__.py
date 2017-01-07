"""
Flask Documentation:     http://flask.pocoo.org/docs/
Jinja2 Documentation:    http://jinja.pocoo.org/2/documentation/
Werkzeug Documentation:  http://werkzeug.pocoo.org/documentation/

"""
import os
from flask import Flask, render_template, request, redirect, url_for, session, Markup
import sys

reload(sys)
sys.setdefaultencoding('utf8')

app = Flask(__name__)

if __name__ == "__main__":
    app.run()
