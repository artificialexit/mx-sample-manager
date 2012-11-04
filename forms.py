from wtforms import Form, BooleanField, TextField, SelectField, validators

class SampleForm(Form):
    name = TextField('Name')
    project = SelectField('Project')
    
class ProjectForm(Form):
    name = TextField('Name')

class HolderForm(Form):
    name = TextField('Name')
    type = SelectField('Type', choices=[(u'Puck', 'Puck'), (u'Cassette', 'Cassette')])