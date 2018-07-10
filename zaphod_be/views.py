from django.http import HttpResponseNotAllowed, HttpResponseNotFound, HttpResponseRedirect

from zaphod_be.tasks import do_reload_uwsgi

try:
    # noinspection PyPackageRequirements
    import uwsgi
except ImportError:
    uwsgi = None


def reload_uwsgi(request):
    if request.method != "POST":
        return HttpResponseNotAllowed(['POST'])

    if not uwsgi:
        return HttpResponseNotFound("Not running under UWSGI")

    do_reload_uwsgi()
    return HttpResponseRedirect(request.POST.get('next', '/admin/'))
