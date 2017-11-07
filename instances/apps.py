from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class InstancesConfig(AppConfig):
    name = 'instances'
    verbose_name = _('Test-cluster instances')
