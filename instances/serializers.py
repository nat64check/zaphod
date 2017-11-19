from rest_framework import serializers

from instances.models import Trillian, Marvin


class TrillianSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Trillian
        fields = ('id', 'name', 'admin', 'admin_id',
                  'hostname', 'is_active', 'version', 'country', 'location', 'marvins', 'marvin_ids',
                  '_url')


class MarvinSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Marvin
        fields = ('id', 'trillian', 'trillian_id',
                  'name', 'hostname', 'type', 'version',
                  'browser_name', 'browser_version', 'instance_type', 'addresses',
                  '_url')
