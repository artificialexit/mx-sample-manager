import os
import collections
from pytz import timezone

from flask import Flask, send_from_directory, render_template
from flask.ext.mongokit import MongoKit
from flask.ext.pymongo import PyMongo

from . import config

app = Flask(__name__)
app.config.from_object(config)

db = MongoKit(app)
mongo = PyMongo(app, config_prefix='MONGODB')
localtime = timezone("Australia/Melbourne")

@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'),
                               'favicon.ico', mimetype='image/vnd.microsoft.icon')

@app.context_processor
def inject_navigation():
    navigation = collections.OrderedDict({
        #'index': 'Home',
    })
    navigation['projects_list'] = 'Projects'
    navigation['holders_list']  = 'Holders'
    navigation['processing_list']  = 'Processing'

    return dict(nav=navigation)

from . import models
from . import views