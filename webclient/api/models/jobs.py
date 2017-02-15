import json
from bson import ObjectId
from webclient.api.models.schedules import create_schedule, get_schedule
from webclient.dbcontext import db
from webclient.api.utils.pagination import get_paged_documents, parse_url_parameters
from webclient.api.utils.celeryutils import normalize_job_states
from worker.tasks import execute_job, revoke_job


def get_jobs(args, schedule_id=None):
    """
    Returns list of jobs

    :param args: pagination and filtering arguments
    :param schedule_id: schedule ID
    """
    normalize_job_states()
    page, pagesize, sort, filter_arg = parse_url_parameters(args)

    filter_fields = {}

    if schedule_id is not None:
        schedule = get_schedule(schedule_id)

        if not schedule:
            return list()

        previous_runs = schedule['previous_runs']
        filter_fields = {'_id': {'$in': previous_runs}}

    if filter_arg:
        tmp = [{'url': {'$regex': '.*' + filter_arg + '.*', '$options': 'i'}},
               {'name': {'$regex': '.*' + filter_arg + '.*', '$options': 'i'}},
               {'useragent': {'$regex': '.*' + filter_arg + '.*', '$options': 'i'}},
               {'_state': {'$regex': '.*' + filter_arg + '.*', '$options': 'i'}},
               {'type': {'$regex': '.*' + filter_arg + '.*', '$options': 'i'}},
               {'classification': {'$regex': '.*' + filter_arg + '.*', '$options': 'i'}}]

        filter_fields['$or'] = tmp

    jobs = get_paged_documents(db.jobs,
                               page=page,
                               pagesize=pagesize,
                               sort=sort,
                               collums=None,
                               filter_fields=filter_fields)

    json_string = json.dumps(jobs)
    return json_string


def get_job(job_id):
    """
    Returns job with job_id

    :param job_id: job ID
    """
    normalize_job_states()
    job = db.jobs.find_one({'_id': ObjectId(job_id)})

    return job


def create_job(data):
    """
    Creates job

    :param data: job parameters
    :return: job ID
    """
    url = data.get('url')

    if not url:
        raise AttributeError('URL is missing')

    job_name = data.get('name')

    if not job_name:
        raise AttributeError('Name is missing')

    submitter_id = data.get('submitter_id')
    '''
    if submitter_id is None:
        raise AttributeError('Submitter id is missing')
    '''

    job_type = data.get('type') or 'singleurl'
    user_agent = data.get('useragent') or 'winxpie60'
    crawler_time_limit = data.get('crawler_time_limit') or 600
    thug_time_limit = data.get('thug_time_limit') or 600

    eta = data.get('eta')
    cron = data.get('cron')
    interval = data.get('interval')
    max_run_count = data.get('max_run_count') or 100

    args = {
        'referer': data.get('referer'),
        'java': data.get('java'),
        'shockwave': data.get('shockwave'),
        'adobepdf': data.get('adobepdf'),
        'proxy': data.get('proxy'),
        'dom_events': data.get('dom_events'),
        'no_cache': data.get('no_cache') or False,
        'web_tracking': data.get('web_tracking') or False,
        'url_classifiers': data.get('url_classifiers'),
        'html_classifiers': data.get('html_classifiers'),
        'js_classifiers': data.get('js_classifiers'),
        'vb_classifiers': data.get('vb_classifiers'),
        'sample_classifiers': data.get('sample_classifiers'),
        'depth_limit': data.get('depth_limit') or 1,
        'only_internal': data.get('only_internal') or True,
        'allowed_domains': data.get('allowed_domains'),
        'download_delay': data.get('download_delay') or 0,
        'randomize_download_delay': data.get('randomize_download_delay') or False,
        'redirect_max_times': data.get('redirect_max_times') or 30,
        'robotstxt_obey': data.get('robotstxt_obey') or False
    }

    job_data = {
        '_state': 'PENDING',
        '_current_url': None,
        '_error': None,
        'type': job_type,
        'name': job_name,
        'url': url,
        'useragent': user_agent,
        'classification': None,
        'start_time': None,
        'end_time': None,
        'crawler_start_time': None,
        'crawler_end_time': None,
        'crawler_time_limit': crawler_time_limit,
        'thug_time_limit': thug_time_limit,
        'eta': eta,
        'submitter_id': submitter_id,
        'schedule_id': None,
        'args': args,
        'tasks': []
    }

    # Schedule job if cron or interval is present
    if cron or interval:
        create_schedule(task='worker.tasks.execute_job', name=job_name, args=[job_data],
                        max_run_count=max_run_count, run_after=eta, cron=cron, interval=interval)
        return None

    job_id = execute_job.apply(args=[job_data], task_id=str(ObjectId()))
    return job_id.result


def delete_job(job_id):
    """
    Deletes job with specified job_id

    :param job_id: job ID
    :return: True if successful, False otherwise
    """
    return revoke_job(job_id)


def update_job(job_id, data):
    """
    Updates job with specified job_id

    :param job_id: job ID
    :param data: fields to change
    :return: job ID
    """
    job_name = data.get('name')

    db.jobs.update_one({'_id': ObjectId(job_id)}, {'$set': {'name': job_name}})

    return job_id
