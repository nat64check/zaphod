# ••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••
#  Copyright (c) 2018, S.J.M. Steffann. This software is licensed under the BSD
#  3-Clause License. Please see the LICENSE file in the project root directory.
# ••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••

from django.http import HttpResponseForbidden, HttpResponseNotAllowed, HttpResponseNotFound, HttpResponseRedirect

from generic.tasks import do_reload_uwsgi

try:
    # noinspection PyPackageRequirements
    import uwsgi
except ImportError:
    uwsgi = None


def reload_uwsgi(request):
    if not uwsgi:
        return HttpResponseNotFound("Not running under UWSGI")

    if request.method != "POST":
        return HttpResponseNotAllowed(['POST'])

    if not request.user.is_superuser:
        return HttpResponseForbidden("You are not allowed to restart UWSGI")

    do_reload_uwsgi()
    return HttpResponseRedirect(request.POST.get('next', '/admin/'))
