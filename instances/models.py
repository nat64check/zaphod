from django.contrib.gis.db import models
from django_countries.fields import CountryField


class Trillian(models.Model):
    name = models.CharField(max_length=100)
    country = CountryField()
    location = models.PointField(geography=True)

    @property
    def country_flag(self):
        return self.country.unicode_flag if self.country else ''


class Region(models.Model):
    code = models.PositiveIntegerField(primary_key=True)
    parent = models.ForeignKey('self', on_delete=models.CASCADE, blank=True, null=True)
    level = models.PositiveSmallIntegerField()
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ('name',)


class CountryRegion(models.Model):
    region = models.ForeignKey(Region, on_delete=models.CASCADE)
    country = CountryField()
