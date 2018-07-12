from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers

user_model = get_user_model()


# noinspection PyAbstractClass
class PasswordSerializer(serializers.Serializer):
    password = serializers.CharField(required=True, help_text=_('The new password for this user'))


class UserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = user_model
        fields = ('id', 'username', '_url')


class UserAdminSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = user_model
        fields = ('id', 'username', 'first_name', 'last_name', 'email',
                  'is_active', 'date_joined', 'last_login',
                  '_url')
