from uwsgi_tasks import task

try:
    # noinspection PyPackageRequirements
    import uwsgi
except ImportError:
    uwsgi = None


@task(retry_count=1)
def do_reload_uwsgi():
    uwsgi.reload()
