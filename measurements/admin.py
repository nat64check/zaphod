import json
from copy import copy

from django.contrib import admin
from django.contrib.postgres.fields import JSONField
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _
from prettyjson import PrettyJSONWidget
from pygments import highlight
from pygments.formatters.html import HtmlFormatter
from pygments.lexers.data import JsonLexer

from measurements.models import InstanceRun, InstanceRunMessage, InstanceRunResult, Schedule, TestRun, TestRunMessage


@admin.register(Schedule)
class ScheduleAdmin(admin.ModelAdmin):
    list_display = ('name', 'url', 'owner',
                    'time', 'start', 'end', 'frequency',
                    'first_testrun', 'last_testrun', 'is_active',
                    'admin_trillians', 'admin_testruns',
                    'is_public')
    list_filter = (('owner', admin.RelatedOnlyFieldListFilter),)
    search_fields = ('url', 'owner__first_name', 'owner__last_name', 'owner__email', 'name')

    def admin_trillians(self, schedule):
        return ', '.join([trillian.name for trillian in schedule.trillians.all()]) or '-'

    admin_trillians.short_description = _('Trillians')

    def admin_testruns(self, schedule):
        return schedule.testruns.count()

    admin_testruns.short_description = _('Testruns')

    def is_active(self, schedule):
        return schedule.is_active

    is_active.short_description = _('is active')
    is_active.boolean = True


class TestRunMessageAdmin(admin.TabularInline):
    model = TestRunMessage


@admin.register(TestRun)
class TestRunAdmin(admin.ModelAdmin):
    list_display = ('url', 'owner', 'schedule', 'requested', 'started', 'finished', 'analysed')
    list_filter = (('owner', admin.RelatedOnlyFieldListFilter),)
    date_hierarchy = 'requested'
    search_fields = ('url', 'owner__first_name', 'owner__last_name', 'owner__email', 'schedule__name')
    inlines = (TestRunMessageAdmin,)


class InstanceRunMessageAdmin(admin.TabularInline):
    model = InstanceRunMessage


class InlineInstanceRunResult(admin.TabularInline):
    model = InstanceRunResult
    fields = ('marvin', 'when', 'nice_ping_response', 'nice_web_response', 'data_image')
    readonly_fields = ('marvin', 'when', 'nice_ping_response', 'nice_web_response', 'data_image')
    extra = 0
    can_delete = False
    show_change_link = True

    formfield_overrides = {
        JSONField: {'widget': PrettyJSONWidget(attrs={'initial': 'parsed'})}
    }

    def has_add_permission(self, request):
        return False

    def nice_ping_response(self, instance):
        # Convert the data to sorted, indented JSON
        response = json.dumps(instance.ping_response, indent=2)
        formatter = HtmlFormatter(style='colorful')
        response = highlight(response, JsonLexer(), formatter)
        style = "<style>" + formatter.get_style_defs() + "</style><br>"

        # Safe the output
        return mark_safe(style + response)

    nice_ping_response.short_description = _('ping response')

    def nice_web_response(self, instance):
        # Convert the data to sorted, indented JSON
        data = copy(instance.web_response)
        if data:
            if 'image' in data:
                del data['image']
            if 'resources' in data:
                del data['resources']
        response = json.dumps(data, indent=2)
        formatter = HtmlFormatter(style='colorful')
        response = highlight(response, JsonLexer(), formatter)
        style = "<style>" + formatter.get_style_defs() + "</style><br>"

        # Safe the output
        return mark_safe(style + response)

    nice_web_response.short_description = _('web response')

    def data_image(self, instance):
        try:
            return mark_safe('<img style="width: 300px" src="data:image/png;base64,{}">'.format(
                instance.web_response['image']
            ))
        except (KeyError, TypeError, AttributeError):
            return '-'

    data_image.short_description = _('image')


@admin.register(InstanceRun)
class InstanceRunAdmin(admin.ModelAdmin):
    list_display = ('testrun', 'trillian', 'requested', 'started', 'finished', 'analysed')
    list_filter = (('trillian', admin.RelatedOnlyFieldListFilter),)
    date_hierarchy = 'testrun__requested'
    search_fields = ('testrun__url',
                     'testrun__owner__first_name', 'testrun__owner__last_name', 'testrun__owner__email',
                     'testrun__schedule__name',
                     'trillian__name',)
    autocomplete_fields = ('testrun',)
    inlines = (InstanceRunMessageAdmin, InlineInstanceRunResult)


@admin.register(InstanceRunResult)
class InstanceRunResultAdmin(admin.ModelAdmin):
    list_display = ('instancerun', 'marvin')
    list_filter = (('marvin', admin.RelatedOnlyFieldListFilter),)
    date_hierarchy = 'instancerun__testrun__requested'
    search_fields = ('instancerun__testrun__url',
                     'instancerun__testrun__owner__first_name', 'instancerun__testrun__owner__last_name',
                     'instancerun__testrun__owner__email',
                     'instancerun__testrun__schedule__name',
                     'marvin__trillian__name',)
    autocomplete_fields = ('instancerun',)
