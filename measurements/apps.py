# ••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••
#  Copyright (c) 2018, S.J.M. Steffann. This software is licensed under the BSD
#  3-Clause License. Please see the LICENSE file in the project root directory.
# ••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••

from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class MeasurementsConfig(AppConfig):
    name = 'measurements'
    verbose_name = _('Measurement data')

    def ready(self):
        # noinspection PyUnresolvedReferences
        from . import signals
