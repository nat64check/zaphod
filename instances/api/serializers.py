# ••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••
#  Copyright (c) 2018, S.J.M. Steffann. This software is licensed under the BSD
#  3-Clause License. Please see the LICENSE file in the project root directory.
# ••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••

from rest_framework.serializers import HyperlinkedModelSerializer
from rest_framework_serializer_extensions.serializers import SerializerExtensionsMixin

from instances.models import Marvin, Trillian


class TrillianSerializer(SerializerExtensionsMixin, HyperlinkedModelSerializer):
    class Meta:
        model = Trillian
        fields = ('id', 'name', 'admins',
                  'hostname', 'is_alive', 'version', 'country', 'location',
                  'flag', 'marvins',
                  '_url')
        expandable_fields = dict(
            admins=dict(
                serializer='generic.api.serializers.UserSerializer',
                many=True,
            ),
            marvins=dict(
                serializer='instances.api.serializers.MarvinSerializer',
                many=True,
            )
        )


class MarvinSerializer(SerializerExtensionsMixin, HyperlinkedModelSerializer):
    class Meta:
        model = Marvin
        fields = ('id',
                  'trillian',
                  'name', 'hostname', 'type', 'version',
                  'browser_name', 'browser_version', 'instance_type', 'addresses',
                  'first_seen', 'last_seen',
                  '_url')
        read_only_fields = ('trillian',)

        expandable_fields = dict(
            trillian=TrillianSerializer,
        )
