from . import app, db
from flask.ext.mongokit import MongoKit, Document
from mongokit import ObjectId, IS

class Project(Document):
    __collection__ = 'projects'
    structure = {
        'name': unicode,
        'description': unicode,
        'sequence': unicode,
    }
    required_fields = ['name']
#    default_values = {'creation': datetime.utcnow}
    use_dot_notation = True
    use_schemaless = True
    
class Sample(Document):
    __collection__ = 'samples'
    structure = {
        'name': unicode,
        'description': unicode,
        'project': Project,
        'holder': ObjectId,
        'priority': IS(u'None', u'Low', u'Medium', u'High'),
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

class Processing(Document):
    __collection__ = 'processing'

    structure = {
        'sample': Sample,
        'type': IS(u'indexing', u'dataset'),
        'epn': unicode,
        'resolution': float,
        'space_group': unicode,
        'unit_cell': (float, float, float),
        'no_frames': int,
        'directory': unicode,
        'status': unicode,
        'success': bool,
        'completed': bool
    }

    required_fields = ['sample', 'type', 'epn']
    use_dot_notation = True
    use_schemaless = True
    use_autorefs = True


db.register([Sample, Project, Holder, Processing])

