# ••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••
#  Copyright (c) 2018, S.J.M. Steffann. This software is licensed under the BSD 3-Clause License. Please seel the LICENSE file in the project root directory.
# ••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••

from django.db.models import Q
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django_filters import BooleanFilter, FilterSet
from django_filters.filters import NumberFilter
from django_filters.utils import verbose_lookup_expr

from instances.models import instance_type_choices
from measurements.models import Schedule, TestRun

score_types = [
    ('image_score', _('image score')),
    ('resource_score', _('resource score')),
    ('overall_score', _('overall score')),
]


class ScheduleFilter(FilterSet):
    is_active = BooleanFilter(label=_('is active'), method='is_active_filter')

    class Meta:
        model = Schedule
        fields = {
            'owner': ['exact'],
            'name': ['exact', 'icontains'],
            'url': ['exact', 'icontains'],
            'trillians': ['contains'],
            'start': ['gte', 'lte'],
            'end': ['gte', 'lte', 'isnull'],
            'frequency': ['exact'],
            'is_public': ['exact'],
        }

    # noinspection PyUnusedLocal
    def is_active_filter(self, queryset, name, value):
        now = timezone.now()

        started_before_today = Q(start__lt=now.date())
        started_today = Q(start=now.date(), time__lt=now.time())
        started = started_before_today | started_today

        ended_before_today = Q(end__lt=now.date())
        ended_today = Q(end=now.date(), time__lt=now.time())
        ended = ended_before_today | ended_today

        if value is True:
            return queryset.filter(started & ~ended)
        elif value is False:
            return queryset.filter(~started | ended)

        # We shouldn't get here
        return queryset


class TestRunFilter(FilterSet):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for instance_type in instance_type_choices:
            for score_type in score_types:
                field_name = str(instance_type[0]).replace('-', '_') + '_' + str(score_type[0])
                for lookup_expr in ['gte', 'lte']:
                    self.filters[field_name + '__' + lookup_expr] = NumberFilter(
                        field_name=field_name,
                        label=str(instance_type[1]) + ' ' + str(score_type[1]) + ' ' + verbose_lookup_expr(lookup_expr),
                        lookup_expr=lookup_expr
                    )
                self.filters[field_name + '__isnull'] = BooleanFilter(
                    field_name=field_name,
                    label=str(instance_type[1]) + ' ' + str(score_type[1]) + ' ' + verbose_lookup_expr('isnull'),
                    lookup_expr='isnull'
                )

    class Meta:
        model = TestRun
        fields = {
            'owner': ['exact'],
            'schedule': ['exact'],
            'url': ['exact', 'icontains'],
            'requested': ['gte', 'lte'],
            'started': ['gte', 'lte', 'isnull'],
            'finished': ['gte', 'lte', 'isnull'],
            'analysed': ['gte', 'lte', 'isnull'],
            'is_public': ['exact'],
            'image_score': ['gte', 'lte'],
            'resource_score': ['gte', 'lte'],
            'overall_score': ['gte', 'lte'],
        }
