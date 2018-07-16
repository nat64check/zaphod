import os

import time
from django.db.models import QuerySet
from django.utils.termcolors import colorize


def retry_get(qs: QuerySet, **kwargs):
    for delay in (0.5, 1, 2, 4, None):
        try:
            return qs.get(**kwargs)
        except qs.model.DoesNotExist:
            if delay:
                time.sleep(delay)
            else:
                raise


def print_with_color(msg, **kwargs):
    bold = kwargs.pop('bold', False)
    if bold:
        opts = kwargs.setdefault('opts', [])
        if 'bold' not in opts:
            opts.append('bold')

    pid = os.getpid()
    print(colorize('[spooler {}] {}'.format(pid, msg), **kwargs))


def print_success(msg):
    print_with_color(msg, fg='green', bold=True)


def print_notice(msg):
    print_with_color(msg, fg='white', bold=True)


def print_message(msg):
    print_with_color(msg, fg='white')


def print_warning(msg):
    print_with_color(msg, fg='yellow', bold=True)


def print_error(msg):
    print_with_color(msg, fg='red', bold=True)
