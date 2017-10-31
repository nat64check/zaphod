from django.contrib import admin
from django.contrib.gis.admin.options import OSMGeoAdmin
from django.utils.translation import gettext_lazy as _

from instances.filters import TrillianRegionFilter
from instances.models import Trillian


class SearchableGeoAdmin(OSMGeoAdmin):
    map_template = 'searchable_osm.html'


@admin.register(Trillian)
class TrillianAdmin(SearchableGeoAdmin):
    list_display = ('name', 'hostname', 'version', 'country', 'admin_full_name')
    list_filter = (TrillianRegionFilter,)
    ordering = ('name',)

    def admin_full_name(self, trillian):
        return trillian.admin.get_full_name()

    admin_full_name.short_description = _('admin')
    admin_full_name.admin_order_field = 'admin__first_name'
