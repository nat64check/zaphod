from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _
from rest_framework.fields import CharField, EmailField
from rest_framework.serializers import HyperlinkedModelSerializer, ModelSerializer, Serializer

user_model = get_user_model()


# noinspection PyAbstractClass
class PasswordSerializer(Serializer):
    password = CharField(required=True, help_text=_('The new password for this user'))


# noinspection PyAbstractClass
class AuthCodeSerializer(Serializer):
    code = CharField(required=True, help_text=_('The authentication code to activate this account'))


class UserSerializer(HyperlinkedModelSerializer):
    class Meta:
        model = user_model
        fields = ('id', 'username', '_url')


class UserAdminSerializer(HyperlinkedModelSerializer):
    class Meta:
        model = user_model
        fields = ('id', 'username', 'first_name', 'last_name', 'email',
                  'is_active', 'date_joined', 'last_login',
                  '_url')


class UserRegisterSerializer(ModelSerializer):
    email = EmailField(required=True, max_length=128, help_text=_('email address'))

    class Meta:
        model = user_model
        fields = ('username', 'first_name', 'last_name', 'email', 'password')
