# noinspection PyUnusedLocal
def app_version(request):
    from . import __version__ as my_app_version
    return {'APP_VERSION': my_app_version}
