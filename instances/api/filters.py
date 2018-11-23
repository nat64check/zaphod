# ••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••
#  Copyright (c) 2018, S.J.M. Steffann. This software is licensed under the BSD
#  3-Clause License. Please see the LICENSE file in the project root directory.
# ••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••

from django_filters import BaseCSVFilter, CharFilter, Filter, FilterSet

from instances.models import Marvin, Trillian


class TrillianFilter(FilterSet):
    having_admin = Filter(name="admins", lookup_expr='in')

    class Meta:
        model = Trillian
        fields = {
            'name': ['exact', 'icontains'],
            'hostname': ['exact', 'icontains'],
            'is_alive': ['exact'],
            'country': ['exact'],
            'first_seen': ['gte', 'lte'],
            'last_seen': ['gte', 'lte'],
        }


class CharArrayFilter(BaseCSVFilter, CharFilter):
    pass


class MarvinFilter(FilterSet):
    address = CharArrayFilter(name='addresses', lookup_expr='icontains')

    class Meta:
        model = Marvin
        fields = {
            'trillian': ['exact'],
            'name': ['exact', 'icontains'],
            'hostname': ['exact', 'icontains'],
            'type': ['exact'],
            'first_seen': ['gte', 'lte'],
            'last_seen': ['gte', 'lte'],
        }
