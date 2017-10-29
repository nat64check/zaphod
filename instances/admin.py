from django.contrib import admin
from django.contrib.gis.admin.options import OSMGeoAdmin

from instances.filters import RegionFilter
from instances.models import Trillian, Region, CountryRegion


class SearchableGeoAdmin(OSMGeoAdmin):
    map_template = 'searchable_osm.html'


@admin.register(Trillian)
class TrillianAdmin(SearchableGeoAdmin):
    list_display = ('name', 'country', 'country_flag')
    list_filter = (RegionFilter,)


@admin.register(Region)
class RegionAdmin(admin.ModelAdmin):
    list_display = ('name', 'level', 'parent', 'number_of_countries')
    ordering = ('level', 'parent__name', 'name')

    def number_of_countries(self, region):
        return CountryRegion.objects.filter(region=region).count()


@admin.register(CountryRegion)
class CountryRegionAdmin(admin.ModelAdmin):
    list_display = ('country', 'region')
    list_filter = ('region',)
    ordering = ('country', 'region__name')
