from django.conf import settings
from django.contrib.gis.db import models
from django.contrib.postgres.fields import ArrayField
from django.core.validators import RegexValidator, URLValidator
from django.utils.translation import gettext_lazy as _
from django_countries.fields import CountryField


class TrillianManager(models.Manager):
    def get_by_natural_key(self, name):
        return self.get(name=name)


class Trillian(models.Model):
    objects = TrillianManager()

    name = models.CharField(_('name'), max_length=100, unique=True)
    admin = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name=_('admin'), on_delete=models.PROTECT)
    hostname = models.CharField(_('hostname'), max_length=127, unique=True, validators=[
        RegexValidator(URLValidator.host_re, message=_("Please provide a valid host name"))
    ])

    is_active = models.BooleanField(_('is active'), default=True)
    version = models.PositiveSmallIntegerField(_('version'))

    country = CountryField(_('country'))
    location = models.PointField(_('location'), geography=True)

    class Meta:
        ordering = ('name',)

    def __str__(self):
        return self.name

    def natural_key(self):
        return self.name,


class MarvinManager(models.Manager):
    def get_by_natural_key(self, trillian_name, name):
        return self.get(trillian__name=trillian_name, name=name)


class Marvin(models.Model):
    objects = MarvinManager()

    trillian = models.ForeignKey(Trillian, verbose_name=_('Trillian'), on_delete=models.PROTECT)

    name = models.CharField(_('name'), max_length=100)
    hostname = models.CharField(_('hostname'), max_length=127, unique=True, validators=[
        RegexValidator(URLValidator.host_re, message=_("Please provide a valid host name"))
    ])
    type = models.CharField(_('type'), max_length=50)
    version = ArrayField(models.PositiveSmallIntegerField(), verbose_name=_('version'))

    browser_name = models.CharField(_('browser name'), max_length=150)
    browser_version = ArrayField(models.PositiveSmallIntegerField(), verbose_name=_('browser version'))

    instance_type = models.CharField(_('instance type'), max_length=10, choices=[
        ('ipv4', _('IPv4-only')),
        ('ipv6', _('IPv6-only')),
        ('ds', _('Dual-Stack')),
        ('nat64', _('IPv6 with NAT64')),
    ])
    addresses = ArrayField(models.GenericIPAddressField(), verbose_name=_('addresses'), default=list)

    class Meta:
        unique_together = (('trillian', 'name'),)

    def __str__(self):
        return _('{trillian}: {name}').format(name=self.name, trillian=self.trillian)

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
