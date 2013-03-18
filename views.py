from flask import g, request, redirect, url_for, flash, render_template, json
from . import app, db, mongo, localtime
from .utils import templated, jsonify, request_wants_json
from .forms import SampleForm, ProjectForm, HolderForm
from mongokit import ObjectId
from collections import OrderedDict
from operator import itemgetter
from bson import json_util
from jinja2.exceptions import TemplateNotFound
import time
import redis

def get_real_ip():
    if not request.headers.getlist("X-Forwarded-For"):
        return request.remote_addr
    else:
        return request.headers.getlist("X-Forwarded-For")[0]

# taken from userchange
def from_beamline():
    """Quick check on which beamline request is coming from"""
    config = {'109':'MX1', '108':'MX2'}

    octets = get_real_ip().strip().split(".")

    try:
        if octets[0] == '10':
            return config[octets[1]]
    except KeyError:
        pass

redisclient = {'MX1':redis.StrictRedis('10.109.24.2'),
               'MX2':redis.StrictRedis('10.108.24.2')}
# get epn
def get_epn():
    try:
        return redisclient[from_beamline()].get('CURRENT_EPN')
    except KeyError:
        return

## -- SAMPLES -- ##
@app.route("/samples")
@templated()
def samples_list():
    return dict(samples=db.Sample.find())

def samples_form(_id=None, project_id=None):
    if _id:
        sample = db.Sample.get_from_id(_id)
    else:
        sample = db.Sample()
    
    form = SampleForm(request.form, sample)
    form.project.choices = [(project._id, project.name) for project in db.Project.find()]
    
    if len(form.project.choices) == 0:
        raise Exception('Cannot add samples no projects defined')
    
    if _id:
        form.project.data = form.project.coerce(sample.project._id)    
    
    
    if request.method == 'POST':
        sample.name = form.name.data
        sample.description = form.description.data
        sample.priority = form.priority.data
        if project_id:
            sample.project = db.Project.get_from_id(project_id)
        else:
            sample.project = db.Project.get_from_id(ObjectId(form.project.data))
        sample.save()
        return (True, sample.name)   
    return (False, form)
        
    
@app.route('/samples/add', methods=['GET', 'POST'])
@templated('samples/form.twig.html')
def samples_add():
    try:
        status, data = samples_form()
    except Exception, e:
        flash(str(e), 'error')
        return redirect(url_for('samples_list'))
    if status:        
        flash('Sample <strong>%s</strong> added' % (data), 'success')
        return redirect(url_for('samples_list'))
    return dict(form=data, page='Add', submit='Add')

@app.route('/samples/edit/<ObjectId:_id>', methods=['GET', 'POST'])
@templated('samples/form.twig.html')
def samples_edit(_id):
    status, data = samples_form(_id)
    if status:        
        flash('Sample <strong>%s</strong> updated' % (data), 'success')
        return redirect(url_for('samples_list'))
    return dict(form=data, page='Edit', submit='Update')

@app.route("/samples/delete/<_id>")
def samples_delete(_id):
    sample = db.Sample.get_from_id(ObjectId(_id))
    flash('Sample <strong>%s</strong> deleted' % (sample.name, ), 'success')
    sample.delete()
    return redirect(url_for('samples_list'))


## -- Projects -- ##
@app.route("/projects")
@templated()
def projects_list():
    return dict(projects=db.Project.find())

def projects_form(_id=None):
    if _id:
        project = db.Project.get_from_id(_id)
    else:
        project = db.Project()
        
    form = ProjectForm(request.form, project)
    if request.method == 'POST':
        project.name = request.form['name']
        project.description = request.form['description']
        project.sequence = request.form['sequence']
        project.save()
        return (True, project.name)
    return (False, form)

@app.route('/projects/add', methods=['GET', 'POST'])
@templated('projects/form.twig.html')
def projects_add():
    status, data = projects_form()
    if status:
        flash('Project <strong>%s</strong> added' % (data, ), 'success')
        return redirect(url_for('projects_list'))
    return dict(form=data, page='Add', submit='Add')



@app.route('/projects/edit/<ObjectId:_id>', methods=['GET', 'POST'])
@templated('projects/form.twig.html')
def projects_edit(_id):
    status, data = projects_form(_id)
    if status:
        flash('Project <strong>%s</strong> updated' % (data, ), 'success')
        return redirect(url_for('projects_list'))
    return dict(form=data, page='Edit', submit='Update')

@app.route("/projects/delete/<ObjectId:_id>")
def projects_delete(_id):
    project = db.Project.get_from_id(_id)
    #[ item.delete() for item in db.Sample.find({'project.$id':project._id})]
    if db.Sample.find({'project.$id':project._id}).count() > 0:
        flash('Project cant be deleted has referenced samples', 'error')
        return redirect(url_for('projects_list'))
    flash('Project <strong>%s</strong> deleted' % (project.name, ))
    project.delete()
    return redirect(url_for('projects_list'))

## -- Project/Sample -- ##
@app.route("/projects/<ObjectId:project_id>/samples")
@templated()
def projects_samples_list(project_id):
    samples=db.Sample.find({'project.$id':project_id})
    project=db.Project.get_from_id(project_id)
    priority_map = {
        u'None': '',
        u'Low': 'label-success',
        u'Medium': 'label-warning',
        u'High': 'label-important',
    }
    return locals()

@app.route('/projects/<ObjectId:project_id>/samples/add', methods=['GET', 'POST'])
@templated('projects/samples/form.twig.html')
def projects_samples_add(project_id):
    try:
        status, data = samples_form(project_id=project_id)
    except Exception, e:
        flash(str(e), 'error')
        return redirect(url_for('projects_samples_list', project_id=project_id))
    if status:        
        flash('Sample <strong>%s</strong> added' % (data), 'success')
        return redirect(url_for('projects_samples_list', project_id=project_id))
    return dict(form=data, page='Add', submit='Add', project_id=project_id)

@app.route('/projects/<ObjectId:project_id>/samples/edit/<ObjectId:_id>', methods=['GET', 'POST'])
@templated('projects/samples/form.twig.html')
def projects_samples_edit(_id, project_id):
    status, data = samples_form(_id)
    if status:        
        flash('Sample <strong>%s</strong> updated' % (data), 'success')
        return redirect(url_for('projects_samples_list', project_id=project_id))
    return dict(form=data, page='Edit', submit='Update', project_id=project_id)

@app.route("/projects/<ObjectId:project_id>/samples/delete/<_id>")
def projects_samples_delete(_id, project_id):
    sample = db.Sample.get_from_id(ObjectId(_id))
    flash('Sample <strong>%s</strong> deleted' % (sample.name, ), 'success')
    sample.delete()
    return redirect(url_for('projects_samples_list', project_id=project_id))

## -- Holders -- ##
@app.route("/holders")
@templated()
def holders_list():
    return dict(holders=db.Holder.find())

@app.route('/holders/add', methods=['GET', 'POST'])
@templated('holders/form.twig.html')
def holders_add():
    form = HolderForm(request.form)
    if request.method == 'POST':
        holder = db.Holder()
        holder.name = form.name.data
        holder.type = form.type.data
        holder.save()
        flash('Holder <strong>%s</strong> added' % (holder.name, ), 'success')
        return redirect(url_for('holders_list'))
    return dict(form=form, page='Add', submit='Add')

@app.route('/holders/view/<ObjectId:_id>')
def holders_view(_id):
    from operator import itemgetter
    
    holder = db.Holder.get_from_id(_id)
    samples = OrderedDict({})

    sorted_samples = sorted(holder.samples, key=itemgetter('position')) 
    for sample in sorted_samples:
        samples[sample['position']] = sample['sample']
    
    if holder.type == 'Puck':
        return holders_view_puck(holder=holder,samples=samples)

    if holder.type == 'Cassette':
        return holders_view_cassette(holder=holder,samples=samples)

def holders_view_puck(**context):
    size = 300   
    pin_radius, coords = generate_puck(size/2.0)
    width = height = pin_radius * 2.0
    
    context.update(coords=coords,
                width=width,
                height=height,
                puck_size=size)
    
    return render_template('holders/puck/view.twig.html', **context)

def holders_view_cassette(**context):
    context.update(letters=dict([(x, str(unichr(65+x))) for x in range(8)]))
    return render_template('holders/cassette/view.twig.html', **context)

@app.route('/holders/<ObjectId:_id>/sample/add/<pos>')
@templated()
def holders_sample_add(_id, pos):
    samples = db.Sample.find({'holder':None})
    if not samples.count() > 0:
        flash('No Samples', 'error')
        return redirect(url_for('holders_view', _id=_id))
    app.logger.info([_id])
    return dict(_id=_id, pos=pos, samples=samples)

@app.route('/holders/<ObjectId:_id>/sample/add/<pos>/<ObjectId:sample_id>')
def holders_sample_add_test(_id, pos, sample_id):
    holder = db.Holder.get_from_id(_id)
    sample = db.Sample.get_from_id(sample_id)
    
    holder.samples.append({
        'position': int(pos),
        'sample':sample
    })
    sample.holder = holder._id
    
    holder.save()
    sample.save()
    return redirect(url_for('holders_view', _id=_id))

@app.route('/holders/<ObjectId:_id>/sample/remove/<pos>/<ObjectId:sample_id>')
def holders_sample_remove_test(_id, pos, sample_id):
    holder = db.Holder.get_from_id(_id)
    
    for item in holder.samples:
        if item['position'] == pos:
            break
    else:
        holder.samples.remove(item)
        item['sample'].holder = None
        holder.save()
        item['sample'].save()
    
    return redirect(url_for('holders_view', _id=_id))

@app.route("/holders/delete/<ObjectId:_id>")
def holders_delete(_id):
    holder = db.Holder.get_from_id(_id)
    flash('Holder <strong>%s</strong> deleted' % (holder.name, ), 'success')
    holder.delete()
    return redirect(url_for('holders_list'))




## stuff for puck
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

## -- PROCESSING -- ##
@app.route("/processing", methods=['GET', 'POST'])
@templated()
def processing_list():
    if request.method == 'POST':
        data = json.loads(unicode(request.data), object_hook=json_util.object_hook)
        _id = mongo.db.processing.insert(data)
        return jsonify(_id=ObjectId(_id))

    if request_wants_json():
        query = {'epn':  request.args.get('epn', get_epn()),
                 'type': request.args.get('type')}
        query = {k:v for k,v in query.iteritems() if v}

        cursor = mongo.db.processing.find(query).sort('_id', -1)
        if not query.get('epn'):
            cursor.limit(50)
        
        items = list(cursor)
        return jsonify(results=items)

    # for the page generation we return nothing
    # on load a json request will build the table
    return {}

@app.route("/processing/<ObjectId:_id>", methods=["GET", "PUT", "PATCH", "DELETE"])
def processing_obj(_id):
    if request.method == 'GET':
        item = mongo.db.processing.find_one({'_id':_id})
        return jsonify(**item)

    if request.method == 'PATCH':
        data = json.loads(unicode(request.data))
        mongo.db.processing.update({'_id': _id}, {'$set': data})

    if request.method == 'DELETE':
        mongo.db.processing.remove({'_id':_id})

    if request.method == 'PUT':
        data = json.loads(unicode(request.data), object_hook=json_util.object_hook)
        mongo.db.processing.update({'_id': _id}, data, upsert=True)

    return jsonify(result=True)

@app.route("/processing/view/<ObjectId:_id>")
@templated()
def processing_view(_id):
    item = mongo.db.processing.find_one({'_id':_id})
    started_at = localtime.normalize(_id.generation_time.astimezone(localtime))
    item['started_at'] = started_at.strftime('%Y-%m-%d %H:%M:%S %Z')
    item['sample'] = item['sample']['name']
    
    context = dict(item=item, keys=item.keys(), values=item.values())
    context['field_other'] = ['epn', 'started_at', 'status', 'sample', 'directory', 'no_frames', 'last_frame', 'resolution', 'space_group', 'unit_cell']
        
    if str(item['type']) == 'dataset':
        context['field_order'] = [f for f in ['low_resolution_limit','high_resolution_limit', 'completeness', 'i/sigma', 'rmerge', 'rpim(i)', 'multiplicity'] if f in item.keys()]
        context['field_order'].extend(sorted([key for key,value in item.iteritems()
                                              if key not in context['field_order'] and isinstance(value, list) and len(value) <= 3]))
        context['field_other'].append('average_mosaicity')
    if str(item['type']) == 'indexing':
        context['field_other'].extend(['mosaicity', 'indexing_refined_rmsd'])
    
    template = 'processing/view_%s.twig.html' % str(item['type'])
    print [template]
    try:
        return render_template(template, **context)
    except TemplateNotFound:
        print "Failed to find template for %s" % (template, )
        return context
