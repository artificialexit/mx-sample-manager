from wtforms import Form, BooleanField, TextField, TextAreaField, SelectField, validators

class SampleForm(Form):
    name = TextField('Name')
    project = SelectField('Project')
    description = TextAreaField('Description')
    priority = SelectField('Priority', choices=[(u'None', 'None'), (u'Low', 'Low'), (u'Medium', 'Medium'), (u'High', 'High')])
    
class ProjectForm(Form):
    name = TextField('Name')
    description = TextAreaField('Description')
    sequence = TextAreaField('Sequence')

class HolderForm(Form):
    name = TextField('Name')
    type = SelectField('Type', choices=[(u'Puck', 'Puck'), (u'Cassette', 'Cassette')])