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
