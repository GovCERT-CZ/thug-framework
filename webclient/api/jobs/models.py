from uuid import uuid4
from crawler.tasks import crawl_urls
from webclient.dbcontext import db


def get_jobs():
    """
    Method queries every job from database
    :return: list of jobs
    """
    query = db.jobs.find({}, {'_id': 1, '_state': 1, 'base_url': 1, 'depth': 1, 'tasks': 1})

    if query.count() != 0:
        return query

    return list()


def get_job(job_id):
    """
    Method queries single job from database
    :param job_id: Job id
    :return: job with job_id or None
    """
    query = db.jobs.find({'_id': job_id})

    if query.count() != 0:
        return query

    return None


def create_job(data):
    """
    Method starts url crawling and updates database
    :param data:input data
    :return: job id
    """
    uuid = str(uuid4())

    if not data or 'url' not in data:
        return None

    if 'depth' not in data or data['depth'] < 0:
        return None

    if 'only_internal' not in data:
        return None

    json_data = {
        '_id': uuid,
        '_state': 'PENDING',
        'base_url': data['url'],
        'depth': data['depth'],
        'tasks': []
    }

    db.jobs.insert(json_data)

    input_data = {x: data[x] if x in data else ''
                  for x in ['useragent', 'url', 'java', 'shockwave', 'adobepdf', 'proxy', 'depth', 'only_internal']}

    job = crawl_urls.apply_async(args=[input_data], task_id=uuid)
    return job.id


def delete_job(job_id):
    """
    Method deletes job
    TODO
    :param job_id: job id
    """
    pass


def update_job(job_id, **params):
    """
    Method updates job
    TODO
    :param job_id: job id
    :param params: new parameters
    """
    pass


def pause_job(job_id):
    """
    Method pauses job
    TODO
    :param job_id: job id
    """
    pass
