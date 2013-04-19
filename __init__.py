import os
import collections
from pytz import timezone

from flask import Flask, send_from_directory, render_template, redirect, url_for

from .plugins import db, mongo, vbl, beamline
from . import config

app = Flask(__name__)
app.config.from_object(config)

from .reversed import ReverseProxied
app.wsgi_app = ReverseProxied(app.wsgi_app)

db.init_app(app)
mongo.init_app(app, config_prefix='MONGODB')
vbl.init_app(app)
beamline.init_app(app)
localtime = timezone("Australia/Melbourne")

@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'),
                               'favicon.ico', mimetype='image/vnd.microsoft.icon')

@app.context_processor
def inject_navigation():
    return dict(nav=app.config['NAVIGATION'])

@app.context_processor
def inject_title():
    return dict(title=app.config.get('TITLE'))

from . import models
from . import views
from .projects import views
from .processing.views import processing
app.register_blueprint(processing)

@app.route("/")
def index():
    return redirect(url_for(app.config['INDEX_ENDPOINT']))
