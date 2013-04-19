from flask import request, json, render_template
from jinja2.exceptions import TemplateNotFound
from bson import ObjectId, json_util

from .. import app, localtime
from ..plugins import mongo, vbl, beamline
from ..utils import templated, jsonify, request_wants_json


@app.route("/processing/epns")
@vbl.requires_auth
@templated()
def processing_epns():
    return {}


@app.route("/processing", methods=['GET', 'POST'])
@templated()
def processing_list():
    if request.method == 'POST':
        data = json.loads(unicode(request.data), object_hook=json_util.object_hook)
        _id = mongo.db.processing.insert(data)
        return jsonify(_id=ObjectId(_id))

    if request_wants_json():
        query = {'epn':  request.args.get('epn', beamline.EPN),
                 'type': request.args.get('type')}
        query = {k: v for k, v in query.iteritems() if v}

        cursor = mongo.db.processing.find(query).sort('_id', -1)

        limit = request.args.get('limit')
        if limit:
            cursor.limit(int(limit))
        elif not query.get('epn'):
            cursor.limit(50)

        items = list(cursor)
        return jsonify(results=items)

    # for the page generation we return nothing
    # on load a json request will build the table
    return {}


@app.route("/processing/<ObjectId:_id>", methods=["GET", "PUT", "PATCH", "DELETE"])
def processing_obj(_id):
    if request.method == 'GET':
        item = mongo.db.processing.find_one({'_id': _id})
        return jsonify(**item)

    if request.method == 'PATCH':
        data = json.loads(unicode(request.data))
        mongo.db.processing.update({'_id': _id}, {'$set': data})

    if request.method == 'DELETE':
        mongo.db.processing.remove({'_id': _id})

    if request.method == 'PUT':
        data = json.loads(unicode(request.data), object_hook=json_util.object_hook)
        mongo.db.processing.update({'_id': _id}, data, upsert=True)

    return jsonify(result=True)


@app.route("/processing/view/<ObjectId:_id>")
@templated()
def processing_view(_id):
    item = mongo.db.processing.find_one({'_id': _id})
    started_at = localtime.normalize(_id.generation_time.astimezone(localtime))
    item['started_at'] = started_at.strftime('%Y-%m-%d %H:%M:%S %Z')
    item['sample'] = item['sample']['name']

    context = dict(item=item, keys=item.keys(), values=item.values())
    context['field_other'] = ['epn', 'started_at', 'status', 'sample', 'directory', 'no_frames', 'last_frame', 'resolution', 'space_group', 'unit_cell']

    if str(item['type']) == 'dataset':
        context['field_order'] = [f for f in ['low_resolution_limit', 'high_resolution_limit', 'completeness', 'i/sigma', 'rmerge', 'rpim(i)', 'multiplicity'] if f in item.keys()]
        context['field_order'].extend(sorted([key for key, value in item.iteritems()
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
