from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _
from rest_framework import viewsets, serializers, permissions, response, status, decorators

from zaphod_be.filters import UserFilter
from zaphod_be.serializers import UserSerializer

user_model = get_user_model()


# noinspection PyAbstractClass
class PasswordSerializer(serializers.Serializer):
    password = serializers.CharField(required=True, help_text=_('The new password for this user'))


class UserViewSet(viewsets.ModelViewSet):
    queryset = user_model.objects.all()
    permission_classes = (permissions.IsAdminUser,)
    serializer_class = UserSerializer
    filter_class = UserFilter

    # noinspection PyUnusedLocal
    @decorators.detail_route(methods=['post'],
                             permission_classes=[permissions.IsAdminUser],
                             serializer_class=PasswordSerializer)
    def set_password(self, request, pk=None):
        """
        Set a new password for the specified user.
        """
        user = self.get_object()
        serializer = PasswordSerializer(data=request.data)
        if serializer.is_valid():
            user.set_password(serializer.data['password'])
            user.save()
            return response.Response({'status': 'password set'})
        else:
            return response.Response(serializer.errors,
                                     status=status.HTTP_400_BAD_REQUEST)
