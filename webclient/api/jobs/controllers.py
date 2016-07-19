from bson import json_util
from flask import Blueprint, abort, jsonify, request, Response
from webclient.api.jobs.models import get_job, get_jobs, create_job, delete_job

jobs_blueprint = Blueprint('jobs', __name__, url_prefix='/jobs')


@jobs_blueprint.route('/', methods=['GET'])
def get_jobs_controller():
    jobs = get_jobs()

    response = Response(json_util.dumps({'jobs': jobs}, default=json_util.default),
                        mimetype='application/json')

    return response


@jobs_blueprint.route('/<job_id>', methods=['GET'])
def get_jobs_controller(job_id):
    job = get_job(job_id)

    if job is None:
        abort(400)

    response = Response(json_util.dumps({'job': job}, default=json_util.default),
                        mimetype='application/json')

    return response


@jobs_blueprint.route('/', methods=['POST'])
def create_job_controller():
    if not request.json or 'url' not in request.json:
        abort(400)

    job_id = create_job(request.json)

    return jsonify({'job': job_id}), 201


@jobs_blueprint.route('/<job_id>', methods=['DELETE'])
def delete_job_controller(job_id):
    delete_job(job_id)
    return jsonify(None)
