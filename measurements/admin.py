from django.contrib import admin

from measurements.models import Schedule, TestRun, InstanceRun, InstanceRunResult, TestRunMessage, InstanceRunMessage


@admin.register(Schedule)
class TestScheduleAdmin(admin.ModelAdmin):
    list_display = ('name', 'url', 'owner', 'time', 'start', 'end', 'frequency', 'is_public')
    list_filter = (('owner', admin.RelatedOnlyFieldListFilter),)
    search_fields = ('url', 'owner__first_name', 'owner__last_name', 'owner__email', 'name')


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
    list_display = ('instance', 'marvin')
    list_filter = (('marvin', admin.RelatedOnlyFieldListFilter),)
    date_hierarchy = 'instance__requested'
    search_fields = ('instance__testrun__url',
                     'instance__testrun__owner__first_name', 'instance__testrun__owner__last_name',
                     'instance__testrun__owner__email',
                     'instance__testrun__schedule__name',
                     'marvin__trillian__name',)
    autocomplete_fields = ('instance',)
