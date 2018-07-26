from django.db.models import Q
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django_filters import BooleanFilter, FilterSet

from measurements.models import Schedule


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
