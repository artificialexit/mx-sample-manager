from . import app, db
from flask.ext.mongokit import MongoKit, Document
from mongokit import ObjectId, IS

class Project(Document):
    __collection__ = 'projects'
    structure = {
        'name': unicode,
    }
    required_fields = ['name']
#    default_values = {'creation': datetime.utcnow}
    use_dot_notation = True
    use_schemaless = True
    
class Sample(Document):
    __collection__ = 'samples'
    structure = {
        'name': unicode,
        'project': Project,
        'holder': ObjectId,
        'extra': unicode,
    }
    required_fields = ['name', 'project']
#    default_values = {'creation': datetime.utcnow}
    use_dot_notation = True
    use_schemaless = True
    use_autorefs = True

class Holder(Document):
    __collection__ = 'holders'
    structure = {
        'name': unicode,
        'type': IS(u'Puck', u'Cassette'),
        'samples': [{
            'position':int,
            'sample':Sample
        }]
    }
    required_fields = ['name', 'type']
    use_dot_notation = True
    use_schemaless = True
    use_autorefs = True

db.register([Sample, Project, Holder])

