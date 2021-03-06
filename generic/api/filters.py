# ••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••
#  Copyright (c) 2018, S.J.M. Steffann. This software is licensed under the BSD
#  3-Clause License. Please see the LICENSE file in the project root directory.
# ••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••

from django.contrib.auth import get_user_model
from django_filters import FilterSet

user_model = get_user_model()


class UserFilter(FilterSet):
    class Meta:
        model = user_model
        fields = {
            'username': ['exact'],
        }


class UserAdminFilter(FilterSet):
    class Meta:
        model = user_model
        fields = {
            'username': ['exact', 'icontains'],
            'email': ['exact', 'icontains'],
            'first_name': ['exact', 'icontains'],
            'last_name': ['exact', 'icontains'],
            'is_active': ['exact'],
            'is_staff': ['exact'],
            'date_joined': ['gte', 'lte'],
        }
