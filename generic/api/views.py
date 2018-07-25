from datetime import timedelta

from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.utils.crypto import salted_hmac
from django.utils.translation import gettext_lazy as _
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.serializers import AuthTokenSerializer
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError as RestValidationError
from rest_framework.permissions import AllowAny, DjangoModelPermissionsOrAnonReadOnly
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.settings import api_settings
from rest_framework.viewsets import ModelViewSet, ViewSet
from rest_framework_serializer_extensions.views import SerializerExtensionsAPIViewMixin

from generic.api.filters import UserAdminFilter, UserFilter
from generic.api.permissions import AllowSelf
from generic.api.serializers import (AuthCodeSerializer, PasswordSerializer, UserAdminSerializer,
                                     UserRegisterSerializer,
                                     UserSerializer)
from zaphod_be import __version__ as version

user_model = get_user_model()


class InfoViewSet(SerializerExtensionsAPIViewMixin, ViewSet):
    """
    Generic information about this server.

    list:
    Retrieve an overview of server information.
    """
    permission_classes = (AllowAny,)

    def list(self, request):
        return Response({
            "version": version.split('.'),
            "you": UserAdminSerializer(request.user, context={'request': request}).data,
        })


class UserViewSet(SerializerExtensionsAPIViewMixin, ModelViewSet):
    """
    Management of API users.

    list:
    Retrieve a list of users.

    create:
    Create a new user.

    retrieve:
    Retrieve the details of a single user.

    update:
    Update all the properties of a user.

    partial_update:
    Change one or more properties of a user.

    destroy:
    Deactivate a user.

    register:
    Register a new user.

    set_password:
    Set a new password for the specified user.

    get_token:
    Return the token for the provided username and password.
    """
    permission_classes = (DjangoModelPermissionsOrAnonReadOnly,)

    @property
    def filter_class(self):
        if self.request.user.is_staff:
            # Admin can filter on many properties
            return UserAdminFilter
        else:
            # Others can only filter on exact username
            return UserFilter

    def get_serializer_class(self):
        if not self.request:
            # Docs get the serializer without having a request
            return UserAdminSerializer

        if self.request.user.is_staff:
            # Admin sees all
            return UserAdminSerializer
        else:
            # Others only see minimal details
            return UserSerializer

    def get_queryset(self):
        if self.request.user.is_staff:
            # Admin sees all
            return user_model.objects.all()
        else:
            # Others see active users
            return user_model.objects.filter(is_active=True)

    @action(detail=False,
            methods=['post'],
            permission_classes=[AllowAny],
            get_serializer_class=lambda: UserRegisterSerializer)
    def register(self, request: Request):
        serializer = UserRegisterSerializer(data=request.data, context={'request': request})
        serializer.is_valid()

        errors = serializer.errors

        # Avoid confusion: don't allow registration for existing email addresses through the API
        email = serializer.data.get('email')
        if email and user_model.objects.filter(email=email).exists():
            errors.setdefault('email', []).append(_("A user with this email address already exists."))

        password = serializer.validated_data.pop('password', '')
        try:
            validate_password(password)
        except ValidationError as ex:
            errors.setdefault('password', []).extend(ex.messages)

        # Show errors if there are any
        if errors:
            raise RestValidationError(errors)

        # Create a new user
        user = user_model.objects.create(is_active=False, password=make_password(password), **serializer.validated_data)

        # Use the new user's token to create the authentication code
        token, created = Token.objects.get_or_create(user=user)
        hmac = salted_hmac(user.username, token.key)
        code = hmac.hexdigest()

        try:
            user.email_user("Confirmation code", "Your code is {code}".format(code=code))
        except OSError:
            pass

        return Response(status=201, data=UserAdminSerializer(user, context={'request': request}).data)

    @action(detail=True,
            methods=['post'],
            permission_classes=[AllowAny],
            get_queryset=lambda: user_model.objects.all(),
            get_serializer_class=lambda: AuthCodeSerializer)
    def authenticate(self, request, pk):
        user = self.get_object()
        serializer = AuthCodeSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # Don't activate accounts that are already active, that's silly
        if user.is_active:
            return Response({'status': 'account has already been activated'})

        # Don't reactivate accounts that have been used, we might have deactivated them for some other reason
        if user.last_login:
            raise RestValidationError({
                api_settings.NON_FIELD_ERRORS_KEY: [_('Account cannot be activated')]
            })

        # Use the user's token to create the authentication code
        token, created = Token.objects.get_or_create(user=user)
        hmac = salted_hmac(user.username, token.key)
        code = hmac.hexdigest()

        if serializer.validated_data['code'] != code:
            raise RestValidationError({
                'code': [_('Invalid authentication code, account not activated')]
            })

        if user.date_joined < timezone.now() - timedelta(days=7):
            raise RestValidationError({
                'code': [_('Authentication code expired, account not activated')]
            })

        user.is_active = True
        user.save(update_fields=['is_active'])

        return Response({'status': 'account activated'})

    @action(detail=False,
            methods=['post'],
            permission_classes=[AllowAny],
            get_serializer_class=lambda: AuthTokenSerializer)
    def get_token(self, request):
        serializer = AuthTokenSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)

        # Get the user and get/create their token
        user = serializer.validated_data['user']
        token, created = Token.objects.get_or_create(user=user)

        # Also treat this as a login
        user.last_login = timezone.now()
        user.save(update_fields=['last_login'])

        return Response({'token': token.key})

    # noinspection PyUnusedLocal
    @action(detail=True,
            methods=['post'],
            permission_classes=[AllowSelf],
            get_serializer_class=lambda: PasswordSerializer)
    def set_password(self, request, pk=None):
        user = self.get_object()
        serializer = PasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user.set_password(serializer.data['password'])
        user.save()
        return Response({'status': 'password set'})

    def perform_destroy(self, instance):
        instance.is_active = False
        instance.save()
