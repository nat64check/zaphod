from django.conf import settings
from django.contrib.gis.db import models
from django.core.validators import RegexValidator, URLValidator
from django.utils.formats import date_format
from django.utils.translation import gettext_lazy as _
from django_countries.fields import CountryField

from zaphod.utils import generate_random_token


class Trillian(models.Model):
    name = models.CharField(max_length=100)
    admin = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)
    hostname = models.CharField(max_length=127, validators=[
        RegexValidator(URLValidator.host_re, message=_("Please provide a valid host name"))
    ])

    is_active = models.BooleanField(default=True)
    version = models.PositiveSmallIntegerField()

    country = CountryField()
    location = models.PointField(geography=True)

    def __str__(self):
        return self.name


class TestSchedule(models.Model):
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)

    name = models.CharField(max_length=100)
    url = models.URLField(db_index=True)

    trillians = models.ManyToManyField(Trillian)

    time = models.TimeField()
    start = models.DateField()
    end = models.DateField(blank=True, null=True)
    frequency = models.CharField(max_length=1, choices=[
        ('D', _('Every day')),
        ('W', _('Every week')),
        ('M', _('Every month')),
    ])

    is_public = models.BooleanField(default=True)

    class Meta:
        unique_together = (('owner', 'name'),)

    def __str__(self):
        return self.name


class TestRun(models.Model):
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, blank=True, null=True, on_delete=models.PROTECT)
    schedule = models.ForeignKey(TestSchedule, blank=True, null=True, on_delete=models.PROTECT)

    url = models.URLField(db_index=True)

    requested = models.DateTimeField(db_index=True)
    started = models.DateTimeField(blank=True, null=True, db_index=True)
    finished = models.DateTimeField(blank=True, null=True, db_index=True)

    is_public = models.BooleanField(default=True)

    def __str__(self):
        if self.finished:
            return '{url} completed on {when}'.format(url=self.url, when=date_format(self.finished, 'DATETIME_FORMAT'))
        elif self.started:
            return '{url} started on {when}'.format(url=self.url, when=date_format(self.started, 'DATETIME_FORMAT'))
        else:
            return '{url} requested on {when}'.format(url=self.url, when=date_format(self.requested, 'DATETIME_FORMAT'))


class TestResult(models.Model):
    testrun = models.ForeignKey(TestRun, on_delete=models.CASCADE)
    trillian = models.ForeignKey(Trillian, on_delete=models.PROTECT)
    id_on_trillian = models.PositiveIntegerField(blank=True, null=True)
    callback_auth_code = models.CharField(max_length=50, default=generate_random_token)

    requested = models.DateTimeField(blank=True, null=True, db_index=True)
    started = models.DateTimeField(blank=True, null=True, db_index=True)
    finished = models.DateTimeField(blank=True, null=True, db_index=True)

    class Meta:
        unique_together = (('testrun', 'trillian'),)

    def __str__(self):
        return '{testrun} on {trillian}'.format(testrun=self.testrun, trillian=self.trillian)
