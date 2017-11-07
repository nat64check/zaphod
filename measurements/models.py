from django.conf import settings
from django.contrib.gis.db import models
from django.contrib.postgres.fields import ArrayField, JSONField
from django.utils.formats import date_format
from django.utils.translation import gettext_lazy as _

from instances.models import Trillian, Marvin
from measurements.utils import generate_random_token


class Schedule(models.Model):
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name=_('owner'), on_delete=models.PROTECT)

    name = models.CharField(_('name'), max_length=100)
    url = models.URLField(_('URL'), db_index=True)

    trillians = models.ManyToManyField(Trillian, verbose_name=_('Trillians'))

    time = models.TimeField(_('time'))
    start = models.DateField(_('start'))
    end = models.DateField(_('end'), blank=True, null=True)
    frequency = models.CharField(_('frequency'), max_length=1, choices=[
        ('D', _('Every day')),
        ('W', _('Every week')),
        ('M', _('Every month')),
    ])

    is_public = models.BooleanField(_('is public'), default=True)

    class Meta:
        verbose_name = _('schedule')
        verbose_name_plural = _('schedules')
        unique_together = (('owner', 'name'),)

    def __str__(self):
        return self.name


class TestRun(models.Model):
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name=_('owner'), blank=True, null=True,
                              on_delete=models.PROTECT)
    schedule = models.ForeignKey(Schedule, verbose_name=_('schedule'), blank=True, null=True, on_delete=models.PROTECT)

    url = models.URLField(_('URL'), db_index=True)

    requested = models.DateTimeField(_('requested'), db_index=True)
    started = models.DateTimeField(_('started'), blank=True, null=True, db_index=True)
    finished = models.DateTimeField(_('finished'), blank=True, null=True, db_index=True)

    is_public = models.BooleanField(_('is public'), default=True)

    image_score = models.FloatField(_('image score'), blank=True, null=True, db_index=True)
    resource_score = models.FloatField(_('resource score'), blank=True, null=True, db_index=True)
    overall_score = models.FloatField(_('overall score'), blank=True, null=True, db_index=True)

    feedback_category = models.PositiveSmallIntegerField(_('feedback category'), blank=True, null=True, choices=[
        (1, _('Error')),
        (5, _('Warning')),
        (10, _('Good')),
    ])
    feedback_text = models.TextField(_('feedback text'), blank=True)

    class Meta:
        verbose_name = _('test run')
        verbose_name_plural = _('test runs')

    def __str__(self):
        if self.finished:
            return _('{url} completed on {when}').format(url=self.url,
                                                         when=date_format(self.finished, 'DATETIME_FORMAT'))
        elif self.started:
            return _('{url} started on {when}').format(url=self.url,
                                                       when=date_format(self.started, 'DATETIME_FORMAT'))
        else:
            return _('{url} requested on {when}').format(url=self.url,
                                                         when=date_format(self.requested, 'DATETIME_FORMAT'))


class Instance(models.Model):
    testrun = models.ForeignKey(TestRun, verbose_name=_('test run'), on_delete=models.CASCADE)
    trillian = models.ForeignKey(Trillian, verbose_name=_('Trillian'), on_delete=models.PROTECT)
    id_on_trillian = models.PositiveIntegerField(_('ID on Trillian'), blank=True, null=True)
    callback_auth_code = models.CharField(_('callback auth code'), max_length=50, default=generate_random_token)

    requested = models.DateTimeField(_('requested'), blank=True, null=True, db_index=True)
    started = models.DateTimeField(_('started'), blank=True, null=True, db_index=True)
    finished = models.DateTimeField(_('finished'), blank=True, null=True, db_index=True)

    dns_results = ArrayField(models.GenericIPAddressField(), verbose_name=_('DNS results'), blank=True, default=list)

    class Meta:
        verbose_name = _('instance')
        verbose_name_plural = _('instances')
        unique_together = (('testrun', 'trillian'),)

    def __str__(self):
        return _('{testrun} on {trillian}').format(testrun=self.testrun, trillian=self.trillian)


class InstanceResult(models.Model):
    instance = models.ForeignKey(Instance, verbose_name=_('instance'), on_delete=models.CASCADE)
    marvin = models.ForeignKey(Marvin, verbose_name=_('Marvin'), on_delete=models.PROTECT)

    pings = JSONField()
    web_response = JSONField()

    class Meta:
        verbose_name = _('instance result')
        verbose_name_plural = _('instance results')

    def __str__(self):
        return _('{testrun} on {marvin}').format(testrun=self.instance.testrun, marvin=self.marvin)
