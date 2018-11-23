# ••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••
#  Copyright (c) 2018, S.J.M. Steffann. This software is licensed under the BSD
#  3-Clause License. Please see the LICENSE file in the project root directory.
# ••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••

from uwsgi_tasks import task

try:
    # noinspection PyPackageRequirements
    import uwsgi
except ImportError:
    uwsgi = None


@task(retry_count=1)
def do_reload_uwsgi():
    uwsgi.reload()
