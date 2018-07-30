from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class SelfTestConfig(AppConfig):
    name = 'self_test'
    verbose_name = _('Self-test')
