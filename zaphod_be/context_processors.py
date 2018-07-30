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
