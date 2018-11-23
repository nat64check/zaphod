# ••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••
#  Copyright (c) 2018, S.J.M. Steffann. This software is licensed under the BSD
#  3-Clause License. Please see the LICENSE file in the project root directory.
# ••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••

from django.conf import settings
from django.contrib.gis.db import models
from django.contrib.humanize.templatetags.humanize import naturaltime
from django.contrib.postgres.fields import ArrayField
from django.core.validators import RegexValidator, URLValidator
from django.utils.translation import gettext_lazy as _
from django_countries.fields import CountryField

instance_type_choices = [
    ('dual-stack', _('Dual-stack')),
    ('v4only', _('IPv4-only')),
    ('v6only', _('IPv6-only')),
    ('nat64', _('IPv6 with NAT64')),
]

instance_types = dict(instance_type_choices)


class TrillianManager(models.Manager):
    def get_by_natural_key(self, name):
        return self.get(name=name)


class Trillian(models.Model):
    objects = TrillianManager()

    name = models.CharField(_('name'), max_length=100, unique=True)
    admins = models.ManyToManyField(settings.AUTH_USER_MODEL, verbose_name=_('admins'))
    hostname = models.CharField(_('hostname'), max_length=127, unique=True, validators=[
        RegexValidator(URLValidator.host_re, message=_("Please provide a valid host name"))
    ])
    token = models.CharField(_("token"), max_length=40)

    first_seen = models.DateTimeField(_('first seen'), auto_now_add=True)
    last_seen = models.DateTimeField(_('last seen'))

    is_alive = models.BooleanField(_('is alive'), default=True)
    version = ArrayField(models.PositiveSmallIntegerField(), verbose_name=_('version'))

    country = CountryField(_('country'), db_index=True)
    location = models.PointField(_('location'), geography=True)

    class Meta:
        ordering = ('name',)

    def __str__(self):
        return self.name

    def natural_key(self):
        return self.name,

    def marvin_ids(self):
        return self.marvins.values_list('id', flat=True)

    def flag(self):
        return self.country.unicode_flag

    def display_version(self):
        return '.'.join(map(str, self.version))

    display_version.short_description = _('version')
    display_version.admin_order_field = 'version'

    def last_seen_display(self):
        return naturaltime(self.last_seen)

    last_seen_display.short_description = _('last seen')
    last_seen_display.admin_order_field = 'last_seen'


class MarvinManager(models.Manager):
    def get_by_natural_key(self, trillian_name, name):
        return self.get(trillian__name=trillian_name, name=name)


class Marvin(models.Model):
    objects = MarvinManager()

    trillian = models.ForeignKey(Trillian, verbose_name=_('Trillian'), related_name='marvins', on_delete=models.PROTECT)

    name = models.CharField(_('name'), max_length=100)
    hostname = models.CharField(_('hostname'), max_length=127, validators=[
        RegexValidator(URLValidator.host_re, message=_("Please provide a valid host name"))
    ])
    type = models.CharField(_('type'), max_length=50)
    version = ArrayField(models.PositiveSmallIntegerField(), verbose_name=_('version'))

    browser_name = models.CharField(_('browser name'), max_length=150)
    browser_version = ArrayField(models.PositiveSmallIntegerField(), verbose_name=_('browser version'))

    instance_type = models.CharField(_('instance type'), max_length=10, choices=instance_type_choices)
    addresses = ArrayField(models.GenericIPAddressField(), verbose_name=_('addresses'), default=list)

    first_seen = models.DateTimeField(_('first seen'))
    last_seen = models.DateTimeField(_('last seen'))

    class Meta:
        unique_together = [('trillian', 'name')]
        ordering = ('trillian', 'name',)

    def __str__(self):
        return _('{name} ({type})').format(name=self.name, type=self.instance_type)

    def natural_key(self):
        return self.trillian.name, self.name

    def display_version(self):
        return '.'.join(map(str, self.version))

    display_version.short_description = _('version')
    display_version.admin_order_field = 'version'

    def display_browser_version(self):
        return '.'.join(map(str, self.browser_version))

    display_browser_version.short_description = _('browser version')
    display_browser_version.admin_order_field = 'browser_version'

    def last_seen_display(self):
        return naturaltime(self.last_seen)

    last_seen_display.short_description = _('last seen')
    last_seen_display.admin_order_field = 'last_seen'
