import logging

from django.conf import settings
from django.contrib.gis.db import models
from django.contrib.postgres.fields import ArrayField, JSONField
from django.utils.formats import date_format
from django.utils.translation import gettext_lazy as _

from instances.models import Trillian, Marvin
from measurements.utils import generate_random_token

severities = (
    (logging.CRITICAL, _('Critical')),
    (logging.ERROR, _('Error')),
    (logging.WARNING, _('Warning')),
    (logging.INFO, _('Info')),
    (logging.DEBUG, _('Debug')),
)


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
    image_feedback = models.TextField(_('image feedback'), blank=True)

    resource_score = models.FloatField(_('resource score'), blank=True, null=True, db_index=True)
    resource_feedback = models.TextField(_('resource feedback'), blank=True)

    overall_score = models.FloatField(_('overall score'), blank=True, null=True, db_index=True)
    overall_feedback = models.TextField(_('overall feedback'), blank=True)

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


class TestRunMessage(models.Model):
    testrun = models.ForeignKey(TestRun, on_delete=models.CASCADE)
    severity = models.PositiveSmallIntegerField(_('severity'), choices=severities)
    message = models.CharField(max_length=200)

    class Meta:
        verbose_name = _('test run message')
        verbose_name_plural = _('test run messages')
        ordering = ('testrun', '-severity')

    def __str__(self):
        return '{obj.testrun}: {obj.message} [{obj.severity}]'.format(obj=self)


class InstanceRun(models.Model):
    testrun = models.ForeignKey(TestRun, verbose_name=_('test run'), on_delete=models.CASCADE)
    trillian = models.ForeignKey(Trillian, verbose_name=_('Trillian'), on_delete=models.PROTECT)
    id_on_trillian = models.PositiveIntegerField(_('ID on Trillian'), blank=True, null=True)
    callback_auth_code = models.CharField(_('callback auth code'), max_length=50, default=generate_random_token)

    requested = models.DateTimeField(_('requested'), blank=True, null=True, db_index=True)
    started = models.DateTimeField(_('started'), blank=True, null=True, db_index=True)
    finished = models.DateTimeField(_('finished'), blank=True, null=True, db_index=True)

    dns_results = ArrayField(models.GenericIPAddressField(), verbose_name=_('DNS results'), blank=True, default=list)

    image_score = models.FloatField(_('image score'), blank=True, null=True, db_index=True)
    image_feedback = models.TextField(_('image feedback'), blank=True)

    resource_score = models.FloatField(_('resource score'), blank=True, null=True, db_index=True)
    resource_feedback = models.TextField(_('resource feedback'), blank=True)

    overall_score = models.FloatField(_('overall score'), blank=True, null=True, db_index=True)
    overall_feedback = models.TextField(_('overall feedback'), blank=True)

    class Meta:
        verbose_name = _('instance run')
        verbose_name_plural = _('instance runs')
        unique_together = (('testrun', 'trillian'),)

    def __str__(self):
        return _('{testrun} on {trillian}').format(testrun=self.testrun, trillian=self.trillian)


class InstanceRunMessage(models.Model):
    instancerun = models.ForeignKey(InstanceRun, on_delete=models.CASCADE)
    severity = models.PositiveSmallIntegerField(_('severity'), choices=severities)
    message = models.CharField(max_length=200)

    class Meta:
        verbose_name = _('instance run message')
        verbose_name_plural = _('instance run messages')
        ordering = ('instancerun', '-severity')

    def __str__(self):
        return '{obj.testrun}: {obj.message} [{obj.severity}]'.format(obj=self)


class InstanceRunResult(models.Model):
    instance = models.ForeignKey(InstanceRun, verbose_name=_('instance'), on_delete=models.CASCADE)
    marvin = models.ForeignKey(Marvin, verbose_name=_('Marvin'), on_delete=models.PROTECT)

    pings = JSONField()
    web_response = JSONField()

    class Meta:
        verbose_name = _('instance run result')
        verbose_name_plural = _('instance run results')

    def __str__(self):
        return _('{testrun} on {marvin}').format(testrun=self.instance.testrun, marvin=self.marvin)
