from django.conf import settings
from django.contrib.gis.db import models
from django.core.validators import RegexValidator, URLValidator
from django.utils.translation import gettext_lazy as _
from django_countries.fields import CountryField


class Trillian(models.Model):
    name = models.CharField(max_length=100)
    hostname = models.CharField(max_length=127, validators=[
        RegexValidator(URLValidator.host_re, message=_("Please provide a valid host name"))
    ])
    version = models.PositiveSmallIntegerField()
    admin = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)

    country = CountryField()
    location = models.PointField(geography=True)

    def __str__(self):
        return self.name
