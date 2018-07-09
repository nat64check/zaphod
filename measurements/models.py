import logging

from django.conf import settings
from django.contrib.gis.db import models
from django.contrib.postgres.fields import ArrayField, JSONField
from django.utils import timezone
from django.utils.datetime_safe import date
from django.utils.formats import date_format
from django.utils.translation import gettext_lazy as _

from instances.models import Marvin, Trillian
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

    name = models.CharField(_('name'), max_length=100, help_text=_('Name your test schedule, must be unique'))
    url = models.URLField(_('URL'), db_index=True, help_text=_('The URL you want to test'))

    trillians = models.ManyToManyField(Trillian, verbose_name=_('Trillians'),
                                       help_text=_('The data centres from where you want this URL to be tested'))

    time = models.TimeField(_('time'), help_text=_('The time of day in UTC when you want the tests to be scheduled'))
    start = models.DateField(_('start'), default=date.today,
                             help_text=_('The first day that you want the tests to be run'))
    end = models.DateField(_('end'), blank=True, null=True,
                           help_text=_('The last day that you want the tests to be run'))
    frequency = models.CharField(_('frequency'), max_length=1, choices=[
        ('D', _('Every day')),
        ('W', _('Every week')),
        ('M', _('Every month')),
    ], help_text=_('Frequency to schedule the tests. Can be "D" (daily), "W" (weekly) or "M" (monthly)'))

    is_public = models.BooleanField(_('is public'), default=True,
                                    help_text=_('Whether the test results should be publicly visible'))

    class Meta:
        verbose_name = _('schedule')
        verbose_name_plural = _('schedules')
        ordering = ('start', 'end')
        unique_together = (('owner', 'name'),)

    def __str__(self):
        return self.name

    def trillian_ids(self):
        return self.trillians.values_list('pk', flat=True)

    def testrun_ids(self):
        return self.testruns.values_list('pk', flat=True)


class TestRun(models.Model):
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name=_('owner'), related_name='testruns', blank=True,
                              null=True, on_delete=models.PROTECT)
    schedule = models.ForeignKey(Schedule, verbose_name=_('schedule'), related_name='testruns', blank=True, null=True,
                                 on_delete=models.PROTECT)

    url = models.URLField(_('URL'), db_index=True)

    requested = models.DateTimeField(_('requested'), db_index=True, default=timezone.now)
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
    testrun = models.ForeignKey(TestRun, verbose_name=_('test run'), related_name='messages', on_delete=models.CASCADE)
    severity = models.PositiveSmallIntegerField(_('severity'), choices=severities)
    message = models.CharField(_('message'), max_length=200)

    class Meta:
        verbose_name = _('test run message')
        verbose_name_plural = _('test run messages')
        ordering = ('testrun', '-severity')

    def __str__(self):
        return '{obj.testrun}: {obj.message} [{obj.severity}]'.format(obj=self)

    @property
    def owner(self):
        return self.testrun.owner

    @property
    def owner_id(self):
        return self.testrun.owner_id

    @property
    def is_public(self):
        return self.testrun.is_public


class InstanceRun(models.Model):
    testrun = models.ForeignKey(TestRun, verbose_name=_('test run'), related_name='instanceruns',
                                on_delete=models.CASCADE)
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
        return _('{obj.testrun} on {obj.trillian}').format(obj=self)

    @property
    def owner(self):
        return self.testrun.owner

    @property
    def owner_id(self):
        return self.testrun.owner_id

    @property
    def url(self):
        return self.testrun.url

    @property
    def is_public(self):
        return self.testrun.is_public


class InstanceRunMessage(models.Model):
    instancerun = models.ForeignKey(InstanceRun, verbose_name=_('instance run'), related_name='messages',
                                    on_delete=models.CASCADE)
    severity = models.PositiveSmallIntegerField(_('severity'), choices=severities)
    message = models.CharField(_('message'), max_length=200)

    class Meta:
        verbose_name = _('instance run message')
        verbose_name_plural = _('instance run messages')
        ordering = ('instancerun', '-severity')

    def __str__(self):
        return '{obj.instancerun}: {obj.message} [{obj.severity}]'.format(obj=self)

    @property
    def owner(self):
        return self.instancerun.owner

    @property
    def owner_id(self):
        return self.instancerun.owner_id

    @property
    def is_public(self):
        return self.instancerun.is_public


class InstanceRunResult(models.Model):
    instancerun = models.ForeignKey(InstanceRun, verbose_name=_('instance run'), related_name='results',
                                    on_delete=models.CASCADE)
    marvin = models.ForeignKey(Marvin, verbose_name=_('Marvin'), on_delete=models.PROTECT)

    ping_response = JSONField()
    web_response = JSONField()

    class Meta:
        verbose_name = _('instance run result')
        verbose_name_plural = _('instance run results')

    def __str__(self):
        return _('{obj.instancerun} on {obj.marvin}').format(obj=self)

    @property
    def owner(self):
        return self.instancerun.owner

    @property
    def owner_id(self):
        return self.instancerun.owner_id

    @property
    def is_public(self):
        return self.instancerun.is_public

    @property
    def instance_type(self):
        return self.marvin.instance_type
