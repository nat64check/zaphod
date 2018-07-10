from django.utils.datetime_safe import datetime
from django.utils.timezone import utc


# noinspection PyUnusedLocal
def app_version(request):
    from . import __version__ as my_app_version
    return {'APP_VERSION': my_app_version}


# noinspection PyUnusedLocal
def uwsgi_context(request):
    try:
        # noinspection PyPackageRequirements
        import uwsgi

        return {'UWSGI': {
            'enabled': True,
            'numproc': uwsgi.numproc,
            'buffer_size': uwsgi.buffer_size,
            'started_on': datetime.fromtimestamp(uwsgi.started_on, tz=utc),
            'numworkers': len(uwsgi.workers()),
            'masterpid': uwsgi.masterpid(),
            'total_requests': uwsgi.total_requests(),
            'request_id': uwsgi.request_id(),
            'worker_id': uwsgi.worker_id(),
        }}

    except ImportError:
        return {'UWSGI': {
            'enabled': False,
        }}
