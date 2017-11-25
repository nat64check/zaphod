import django_filters

from instances.models import Trillian, Marvin


class TrillianFilter(django_filters.FilterSet):
    class Meta:
        model = Trillian
        fields = {
            'name': ['exact', 'contains'],
            'hostname': ['exact', 'contains'],
            'admin': ['exact'],
            'is_active': ['exact'],
            'country': ['exact'],
        }


class CharArrayFilter(django_filters.BaseCSVFilter, django_filters.CharFilter):
    pass


class MarvinFilter(django_filters.FilterSet):
    address = CharArrayFilter(name='addresses', lookup_expr='contains')

    class Meta:
        model = Marvin
        fields = {
            'trillian': ['exact'],
            'name': ['exact', 'contains'],
            'hostname': ['exact', 'contains'],
            'type': ['exact'],
        }
