from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from world.models import Region


@admin.register(Region)
class RegionAdmin(admin.ModelAdmin):
    list_display = ('name', 'level', 'parent', 'admin_countries')
    ordering = ('level', 'parent__name', 'name')

    def admin_countries(self, region):
        return ', '.join(sorted([country.name for country in region.countries]))

    admin_countries.short_description = _('countries')
