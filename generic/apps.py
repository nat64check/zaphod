from django.apps import AppConfig


class GenericConfig(AppConfig):
    name = 'generic'

    def ready(self):
        # noinspection PyUnresolvedReferences
        from . import signals
