from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from measurements.models import Schedule, TestRun, InstanceRun, InstanceRunResult, TestRunMessage, InstanceRunMessage


@admin.register(Schedule)
class ScheduleAdmin(admin.ModelAdmin):
    list_display = ('name', 'url', 'owner', 'time', 'start', 'end', 'frequency', 'admin_trillians', 'is_public')
    list_filter = (('owner', admin.RelatedOnlyFieldListFilter),)
    search_fields = ('url', 'owner__first_name', 'owner__last_name', 'owner__email', 'name')

    def admin_trillians(self, schedule):
        return ', '.join([trillian.name for trillian in schedule.trillians.all()]) or '-'

    admin_trillians.short_description = _('Trillians')


class TestRunMessageAdmin(admin.TabularInline):
    model = TestRunMessage


@admin.register(TestRun)
class TestRunAdmin(admin.ModelAdmin):
    list_display = ('url', 'owner', 'schedule', 'requested', 'started', 'finished')
    list_filter = (('owner', admin.RelatedOnlyFieldListFilter),)
    date_hierarchy = 'requested'
    search_fields = ('url', 'owner__first_name', 'owner__last_name', 'owner__email', 'schedule__name')
    inlines = (TestRunMessageAdmin,)


class InstanceRunMessageAdmin(admin.TabularInline):
    model = InstanceRunMessage


@admin.register(InstanceRun)
class InstanceRunAdmin(admin.ModelAdmin):
    list_display = ('testrun', 'trillian', 'id_on_trillian', 'requested', 'started', 'finished')
    list_filter = (('trillian', admin.RelatedOnlyFieldListFilter),)
    date_hierarchy = 'requested'
    search_fields = ('testrun__url',
                     'testrun__owner__first_name', 'testrun__owner__last_name', 'testrun__owner__email',
                     'testrun__schedule__name',
                     'trillian__name',)
    autocomplete_fields = ('testrun',)
    inlines = (InstanceRunMessageAdmin,)


@admin.register(InstanceRunResult)
class InstanceRunResultAdmin(admin.ModelAdmin):
    list_display = ('instancerun', 'marvin')
    list_filter = (('marvin', admin.RelatedOnlyFieldListFilter),)
    date_hierarchy = 'instancerun__requested'
    search_fields = ('instancerun__testrun__url',
                     'instancerun__testrun__owner__first_name', 'instancerun__testrun__owner__last_name',
                     'instancerun__testrun__owner__email',
                     'instancerun__testrun__schedule__name',
                     'marvin__trillian__name',)
    autocomplete_fields = ('instancerun',)
