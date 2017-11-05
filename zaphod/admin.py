from django.contrib import admin
from django.contrib.gis.admin.options import OSMGeoAdmin
from django.forms.models import ModelForm
from django.utils.translation import gettext_lazy as _
from django_countries.widgets import CountrySelectWidget

from zaphod.filters import TrillianRegionFilter
from zaphod.models import Trillian, TestSchedule, TestRun, TestResult


class SearchableGeoAdmin(OSMGeoAdmin):
    map_template = 'searchable_osm.html'


class TrillianAdminForm(ModelForm):
    class Meta:
        model = Trillian
        widgets = {
            'country': CountrySelectWidget(),
        }
        fields = '__all__'


@admin.register(Trillian)
class TrillianAdmin(SearchableGeoAdmin):
    form = TrillianAdminForm
    list_display = ('name', 'hostname', 'version', 'admin_country', 'admin_full_name')
    list_filter = (TrillianRegionFilter,)
    ordering = ('name',)

    def admin_country(self, trillian):
        return '{} {}'.format(trillian.country.unicode_flag, trillian.country.name)

    admin_country.short_description = _('country')
    admin_country.admin_order_field = 'country'

    def admin_full_name(self, trillian):
        return trillian.admin.get_full_name()

    admin_full_name.short_description = _('admin')
    admin_full_name.admin_order_field = 'admin__first_name'


@admin.register(TestSchedule)
class TestScheduleAdmin(admin.ModelAdmin):
    list_display = ('name', 'url', 'owner', 'time', 'start', 'end', 'frequency', 'is_public')


@admin.register(TestRun)
class TestRunAdmin(admin.ModelAdmin):
    list_display = ('url', 'owner', 'schedule', 'requested', 'started', 'finished')


@admin.register(TestResult)
class TestResultAdmin(admin.ModelAdmin):
    list_display = ('testrun', 'trillian', 'id_on_trillian', 'requested', 'started', 'finished')
