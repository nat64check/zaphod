# ••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••
#  Copyright (c) 2018, S.J.M. Steffann. This software is licensed under the BSD 3-Clause License. Please seel the LICENSE file in the project root directory.
# ••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••

import datetime
import logging

from django.conf import settings
from django.contrib.gis.db import models
from django.contrib.postgres.fields import ArrayField, JSONField
from django.utils import timezone
from django.utils.datetime_safe import date
from django.utils.translation import gettext_lazy as _, gettext_noop
from model_utils import FieldTracker

from generic.utils import retry_qs
from instances.models import Marvin, Trillian, instance_type_choices
from measurements.tasks import analyse_instancerun, analyse_instancerunresult, analyse_testrun
from measurements.tasks.cleanup import remove_from_trillian

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

    def first_testrun(self):
        return self.testruns.order_by('requested').values_list('requested', flat=True).first()

    first_testrun.short_description = _('first testrun')
    first_testrun = property(first_testrun)

    def last_testrun(self):
        return self.testruns.order_by('-requested').values_list('requested', flat=True).first()

    last_testrun.short_description = _('last testrun')
    last_testrun = property(last_testrun)

    def is_active(self):
        # Check if it started already
        if datetime.datetime.combine(self.start, self.time, timezone.utc) > timezone.now():
            return False

        # No end means it's still active
        if not self.end:
            return True

        return datetime.datetime.combine(self.end, self.time, timezone.utc) >= timezone.now()

    is_active.short_description = _('is active')
    is_active = property(is_active)


class TestRun(models.Model):
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name=_('owner'), related_name='testruns', blank=True,
                              null=True, on_delete=models.PROTECT)
    schedule = models.ForeignKey(Schedule, verbose_name=_('schedule'), related_name='testruns', blank=True, null=True,
                                 on_delete=models.PROTECT)

    url = models.URLField(_('URL'), db_index=True)

    requested = models.DateTimeField(_('requested'), db_index=True, default=timezone.now)
    started = models.DateTimeField(_('started'), blank=True, null=True, db_index=True)
    finished = models.DateTimeField(_('finished'), blank=True, null=True, db_index=True)
    analysed = models.DateTimeField(_('analysed'), blank=True, null=True, db_index=True)

    is_public = models.BooleanField(_('is public'), default=True)

    image_score = models.FloatField(_('image score'), blank=True, null=True, db_index=True)
    image_feedback = models.TextField(_('image feedback'), blank=True)

    resource_score = models.FloatField(_('resource score'), blank=True, null=True, db_index=True)
    resource_feedback = models.TextField(_('resource feedback'), blank=True)

    overall_score = models.FloatField(_('overall score'), blank=True, null=True, db_index=True)
    overall_feedback = models.TextField(_('overall feedback'), blank=True)

    tracker = FieldTracker(fields=['started', 'finished', 'analysed'])

    class Meta:
        verbose_name = _('test run')
        verbose_name_plural = _('test runs')
        ordering = ('requested',)

    def __str__(self):
        return self.url

    def trillians(self):
        return [instancerun.trillian for instancerun in self.instanceruns.all()]

    trillians.short_description = _('trillians')
    trillians = property(trillians)

    def trigger_analysis(self):
        if self.finished and not self.analysed:
            analyse_testrun(self.pk)


class TestRunAverage(models.Model):
    testrun = models.ForeignKey(TestRun, verbose_name=_('test run'), related_name='averages', on_delete=models.CASCADE)

    instance_type = models.CharField(_('instance type'), max_length=10, choices=instance_type_choices)

    image_score = models.FloatField(_('image score'), blank=True, null=True, db_index=True)
    resource_score = models.FloatField(_('resource score'), blank=True, null=True, db_index=True)
    overall_score = models.FloatField(_('overall score'), blank=True, null=True, db_index=True)

    class Meta:
        verbose_name = _('test run average')
        verbose_name_plural = _('test run averages')
        ordering = ('testrun', 'instance_type')


class TestRunMessage(models.Model):
    testrun = models.ForeignKey(TestRun, verbose_name=_('test run'), related_name='messages', on_delete=models.CASCADE)
    severity = models.PositiveSmallIntegerField(_('severity'), choices=severities)
    message = models.CharField(_('message'), max_length=200)

    class Meta:
        verbose_name = _('test run message')
        verbose_name_plural = _('test run messages')
        ordering = ('testrun', '-severity')

    def __str__(self):
        return '[{obj.severity}] {obj.message}'.format(obj=self)

    def owner(self):
        return self.testrun.owner

    owner.short_description = _('owner')
    owner = property(owner)

    def owner_id(self):
        return self.testrun.owner_id

    owner_id.short_description = _('owner ID')
    owner_id = property(owner_id)

    def is_public(self):
        return self.testrun.is_public

    is_public.short_description = _('is public')
    is_public = property(is_public)


class InstanceRun(models.Model):
    testrun = models.ForeignKey(TestRun, verbose_name=_('test run'), related_name='instanceruns',
                                on_delete=models.CASCADE)
    trillian = models.ForeignKey(Trillian, verbose_name=_('Trillian'), on_delete=models.PROTECT)
    trillian_url = models.URLField(_('Trillian URL'), blank=True)

    started = models.DateTimeField(_('started'), blank=True, null=True, db_index=True)
    finished = models.DateTimeField(_('finished'), blank=True, null=True, db_index=True)
    analysed = models.DateTimeField(_('analysed'), blank=True, null=True, db_index=True)

    dns_results = ArrayField(models.GenericIPAddressField(), verbose_name=_('DNS results'), blank=True, default=list)

    image_score = models.FloatField(_('image score'), blank=True, null=True, db_index=True)
    image_feedback = models.TextField(_('image feedback'), blank=True)

    resource_score = models.FloatField(_('resource score'), blank=True, null=True, db_index=True)
    resource_feedback = models.TextField(_('resource feedback'), blank=True)

    overall_score = models.FloatField(_('overall score'), blank=True, null=True, db_index=True)
    overall_feedback = models.TextField(_('overall feedback'), blank=True)

    tracker = FieldTracker(fields=['started', 'finished', 'analysed'])

    class Meta:
        verbose_name = _('instance run')
        verbose_name_plural = _('instance runs')
        unique_together = (('testrun', 'trillian'),)
        permissions = (
            ("report_back", "Report back on progress"),
        )

    def __str__(self):
        return _('{obj.testrun} on {obj.trillian}').format(obj=self)

    def requested(self):
        return self.testrun.requested

    requested.short_description = _('requested')
    requested = property(requested)

    def owner(self):
        return self.testrun.owner

    owner.short_description = _('owner')
    owner = property(owner)

    def owner_id(self):
        return self.testrun.owner_id

    owner_id.short_description = _('owner ID')
    owner_id = property(owner_id)

    def url(self):
        return self.testrun.url

    url.short_description = _('URL')
    url = property(url)

    def is_public(self):
        return self.testrun.is_public

    is_public.short_description = _('is public')
    is_public = property(is_public)

    def get_baseline(self):
        # We need a dual-stack result as the baseline
        baseline = retry_qs(self.results.filter(marvin__instance_type='dual-stack'))

        if not baseline.exists():
            self.messages.update_or_create(
                severity=logging.CRITICAL,
                message=gettext_noop('No dual-stack result found, impossible to analyse')
            )

        return baseline

    def trigger_analysis(self):
        if self.finished:
            if not self.analysed:
                analyse_instancerun(self.pk)
            else:
                self.testrun.trigger_analysis()

    def trigger_cleanup(self):
        remove_from_trillian(self.pk)


class InstanceRunMessage(models.Model):
    instancerun = models.ForeignKey(InstanceRun, verbose_name=_('instance run'), related_name='messages',
                                    on_delete=models.CASCADE)
    source = models.CharField(_('source'), max_length=1, default='L', choices=(
        ('L', 'Local'),
        ('T', 'Trillian'),
    ))
    severity = models.PositiveSmallIntegerField(_('severity'), choices=severities)
    message = models.CharField(_('message'), max_length=200)

    class Meta:
        verbose_name = _('instance run message')
        verbose_name_plural = _('instance run messages')
        ordering = ('instancerun', '-severity')

    def __str__(self):
        return '[{obj.severity}] {obj.message}'.format(obj=self)

    def owner(self):
        return self.instancerun.owner

    owner.short_description = _('owner')
    owner = property(owner)

    def owner_id(self):
        return self.instancerun.owner_id

    owner_id.short_description = _('owner ID')
    owner_id = property(owner_id)

    def is_public(self):
        return self.instancerun.is_public

    is_public.short_description = _('is public')
    is_public = property(is_public)


class InstanceRunResult(models.Model):
    instancerun = models.ForeignKey(InstanceRun, verbose_name=_('instance run'), related_name='results',
                                    on_delete=models.CASCADE)
    marvin = models.ForeignKey(Marvin, verbose_name=_('Marvin'), on_delete=models.PROTECT)

    when = models.DateTimeField(_('when'))
    analysed = models.DateTimeField(_('analysed'), blank=True, null=True, db_index=True)

    ping_response = JSONField()
    web_response = JSONField()

    image_score = models.FloatField(_('image score'), blank=True, null=True, db_index=True)
    image_feedback = models.TextField(_('image feedback'), blank=True)

    resource_score = models.FloatField(_('resource score'), blank=True, null=True, db_index=True)
    resource_feedback = models.TextField(_('resource feedback'), blank=True)

    overall_score = models.FloatField(_('overall score'), blank=True, null=True, db_index=True)
    overall_feedback = models.TextField(_('overall feedback'), blank=True)

    tracker = FieldTracker(fields=['when', 'analysed'])

    class Meta:
        verbose_name = _('instance run result')
        verbose_name_plural = _('instance run results')

    def __str__(self):
        return _('{obj.instancerun} on {obj.marvin}').format(obj=self)

    def owner(self):
        return self.instancerun.owner

    owner.short_description = _('owner')
    owner = property(owner)

    def owner_id(self):
        return self.instancerun.owner_id

    owner_id.short_description = _('owner ID')
    owner_id = property(owner_id)

    def is_public(self):
        return self.instancerun.is_public

    is_public.short_description = _('is public')
    is_public = property(is_public)

    def instance_type(self):
        return self.marvin.instance_type

    instance_type.short_description = _('instance type')
    instance_type = property(instance_type)

    def trigger_analysis(self):
        if not self.analysed:
            analyse_instancerunresult(self.pk)
        else:
            self.instancerun.trigger_analysis()
