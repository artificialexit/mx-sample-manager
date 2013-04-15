from flask.ext.mongokit import MongoKit
from flask.ext.pymongo import PyMongo
from flask.ext.vbl import VBL
from flask.ext.beamline import Beamline

db = MongoKit()
mongo = PyMongo()
vbl = VBL()
beamline = Beamline()