# ••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••
#  Copyright (c) 2018, S.J.M. Steffann. This software is licensed under the BSD
#  3-Clause License. Please see the LICENSE file in the project root directory.
# ••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••

from django.conf import settings


# noinspection PyUnusedLocal
def app_version(request):
    from . import __version__ as my_app_version
    return {'APP_VERSION': my_app_version}


# noinspection PyUnusedLocal
def my_hostname(request):
    return {
        'MY_HOSTNAME': settings.MY_HOSTNAME,
        'MY_IPV4': settings.MY_IPV4,
        'MY_IPV6': settings.MY_IPV6,
    }
