"""
WSGI config for zaphod_be project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/1.11/howto/deployment/wsgi/
"""
# ••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••
#  Copyright (c) 2018, S.J.M. Steffann. This software is licensed under the BSD
#  3-Clause License. Please see the LICENSE file in the project root directory.
# ••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••

import json
import os
import sys

from django.core.wsgi import get_wsgi_application
from django.utils.translation import gettext as _

from generic.utils import print_success

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "zaphod_be.settings")

application = get_wsgi_application()

# Trigger a dummy request to force loading (and crashing on errors now instead of later)
res = application({
    'REQUEST_METHOD': 'GET',
    'PATH_INFO': '/api/v1/info/',
    'SERVER_NAME': 'localhost',
    'SERVER_PORT': '443',
    'HTTP_ACCEPT': 'application/json',
    'wsgi.url_scheme': 'https',
    'wsgi.version': (1, 0),
    'wsgi.input': sys.stdin,
    'wsgi.errors': sys.stderr,
}, lambda *args, **kwargs: None)

if res.status_code != 200:
    raise RuntimeError("Application could not load")
else:
    content = json.loads(res.content)
    print_success(_("Zaphod {version} has started").format(version='.'.join(content['version'])))
