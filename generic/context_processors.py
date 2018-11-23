# ••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••
#  Copyright (c) 2018, S.J.M. Steffann. This software is licensed under the BSD
#  3-Clause License. Please see the LICENSE file in the project root directory.
# ••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••

from django.utils.datetime_safe import datetime
from django.utils.timezone import utc


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
