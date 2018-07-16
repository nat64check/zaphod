import django_filters

from instances.models import Marvin, Trillian


class TrillianFilter(django_filters.FilterSet):
    having_admin = django_filters.Filter(name="admins", lookup_expr='in')

    class Meta:
        model = Trillian
        fields = {
            'name': ['exact', 'contains'],
            'hostname': ['exact', 'contains'],
            'is_alive': ['exact'],
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
