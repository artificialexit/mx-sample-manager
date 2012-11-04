import os
import collections

from flask import Flask, send_from_directory, render_template
from flask.ext.mongokit import MongoKit

from . import config

app = Flask(__name__)
app.config.from_object(config)

db = MongoKit(app)

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
    navigation['samples_list']  = 'Samples'
    navigation['holders_list']  = 'Holders'

    return dict(nav=navigation)

@app.route('/puck_test/<size>')
def puck_test(size):
    size = int(size)    
    
    pin_radius, coords = generate_puck(size/2.0)
    width = height = pin_radius * 2.0
    
    return render_template('puck_test.html', coords=coords, width=width, height=height, puck_size=size, letters=dict([(x, str(unichr(65+x))) for x in range(8)]))


def generate_xy(radius, count):
    from math import pi, sin, cos
    
    angle = (2.0 * pi) / count
    
    # this is funky so the points get generated in the correct order for numbering
    points = [0] + range(1, count)[::-1]
    
    return [(radius * sin((i * angle) - pi/2),
             radius * cos((i * angle) - pi/2)) for i in points]
    
def generate_puck(radius=200):
    inner_radius = radius * 0.34
    outer_radius = radius * 0.73
    
    inner = generate_xy(inner_radius, 5)
    outer = generate_xy(outer_radius, 11)
    
    pin_radius = round(radius * 0.36, 2) / 2.0
    
    # adjust for top,left position
    offset = radius - pin_radius
    coords = [(i,
               round(x+offset, 2),
               round(y+offset, 2)) for i, (x,y) in enumerate(inner + outer)]
    
    return (pin_radius, coords)
    
    
    

from . import models
from . import views