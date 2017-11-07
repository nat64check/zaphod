from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class WorldConfig(AppConfig):
    name = 'world'
    verbose_name = _('World regions and statistics')
