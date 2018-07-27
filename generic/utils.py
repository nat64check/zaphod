import os

import time
from django.db.models import QuerySet
from django.utils.crypto import get_random_string
from django.utils.termcolors import colorize
from requests.auth import AuthBase


def retry_get(qs: QuerySet, **kwargs):
    for delay in (0.5, 1, 2, 4, None):
        try:
            return qs.get(**kwargs)
        except qs.model.DoesNotExist:
            if delay:
                time.sleep(delay)
            else:
                raise


def retry_all(qs: QuerySet):
    for delay in (0.5, 1, 2, 4, None):
        result = all(qs.all())
        if result:
            return result
        elif delay:
            time.sleep(delay)
        else:
            return False


def print_with_color(msg, **kwargs):
    bold = kwargs.pop('bold', False)
    if bold:
        opts = kwargs.setdefault('opts', [])
        if 'bold' not in opts:
            opts.append('bold')

    pid = os.getpid()
    try:
        # noinspection PyPackageRequirements,PyUnresolvedReferences
        import uwsgi
        master = uwsgi.masterpid()
        worker = uwsgi.worker_id()
        mule = uwsgi.mule_id()
    except ImportError:
        uwsgi = None
        master = 0
        worker = 0
        mule = 0

    if mule:
        print(colorize('[mule {}] {}'.format(mule, msg), **kwargs))
    elif worker:
        print(colorize('[worker {}] {}'.format(worker, msg), **kwargs))
    elif pid == master:
        print(colorize('[master] {}'.format(msg), **kwargs))
    elif uwsgi:
        print(colorize('[spooler {}] {}'.format(pid, msg), **kwargs))
    else:
        print(colorize(msg, **kwargs))


def print_success(msg):
    print_with_color(msg, fg='green', bold=True)


def print_notice(msg):
    print_with_color(msg, fg='cyan', bold=True)


def print_message(msg):
    print_with_color(msg, fg='white', bold=True)


def print_warning(msg):
    print_with_color(msg, fg='yellow', bold=True)


def print_error(msg):
    print_with_color(msg, fg='red', bold=True)


class TokenAuth(AuthBase):
    def __init__(self, token):
        self.token = token

    def __call__(self, req):
        req.headers['Authorization'] = 'Token {}'.format(self.token)
        return req


def generate_random_token():
    return get_random_string(length=50)
