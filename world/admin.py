# ••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••
#  Copyright (c) 2018, S.J.M. Steffann. This software is licensed under the BSD
#  3-Clause License. Please see the LICENSE file in the project root directory.
# ••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••

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
