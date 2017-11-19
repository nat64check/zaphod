import django_filters
from django.contrib.auth import get_user_model

user_model = get_user_model()


class UserFilter(django_filters.FilterSet):
    class Meta:
        model = user_model
        fields = {
            'username': ['exact'],
        }


class UserAdminFilter(django_filters.FilterSet):
    class Meta:
        model = user_model
        fields = {
            'username': ['exact', 'contains'],
            'email': ['exact', 'contains'],
            'first_name': ['exact', 'contains'],
            'last_name': ['exact', 'contains'],
            'is_active': ['exact'],
            'is_staff': ['exact'],
        }
