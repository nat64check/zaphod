from django.conf import settings
from django.contrib.gis.db import models
from django.core.validators import RegexValidator, URLValidator
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

    start = models.DateField()
    end = models.DateField(blank=True, null=True)
    time = models.TimeField()
    frequency = models.CharField(max_length=1, choices=[
        ('D', _('Every day')),
        ('W', _('Every week')),
        ('M', _('Every month')),
    ])

    is_public = models.BooleanField(default=True)


class TestRun(models.Model):
    schedule = models.ForeignKey(TestSchedule, blank=True, null=True, on_delete=models.PROTECT)
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, blank=True, null=True, on_delete=models.PROTECT)

    url = models.URLField(db_index=True)

    requested = models.DateTimeField(db_index=True)
    started = models.DateTimeField(blank=True, null=True, db_index=True)
    finished = models.DateTimeField(blank=True, null=True, db_index=True)

    is_public = models.BooleanField(default=True)


class TestResult(models.Model):
    testrun = models.ForeignKey(TestRun, on_delete=models.CASCADE)
    trillian = models.ForeignKey(Trillian, on_delete=models.PROTECT)
    id_on_trillian = models.PositiveIntegerField(blank=True, null=True)
    callback_auth_code = models.CharField(max_length=50, default=generate_random_token)

    requested = models.DateTimeField(blank=True, null=True, db_index=True)
    started = models.DateTimeField(blank=True, null=True, db_index=True)
    finished = models.DateTimeField(blank=True, null=True, db_index=True)
