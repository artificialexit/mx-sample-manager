from wtforms import Form, BooleanField, TextField, TextAreaField, SelectField, validators

class SampleForm(Form):
    name = TextField('Name')
    project = SelectField('Project')
    description = TextAreaField('Description')
    
class ProjectForm(Form):
    name = TextField('Name')
    description = TextAreaField('Description')
    sequence = TextAreaField('Sequence')

class HolderForm(Form):
    name = TextField('Name')
    type = SelectField('Type', choices=[(u'Puck', 'Puck'), (u'Cassette', 'Cassette')])