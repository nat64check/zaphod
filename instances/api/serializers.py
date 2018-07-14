from rest_framework import serializers

from instances.models import Marvin, Trillian


class TrillianSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Trillian
        fields = ('id', 'name', 'admins',
                  'hostname', 'alive', 'version', 'country', 'location', 'marvins', 'marvin_ids',
                  'flag',
                  '_url')


class MarvinSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Marvin
        fields = ('id', 'trillian', 'trillian_id',
                  'name', 'hostname', 'type', 'version',
                  'browser_name', 'browser_version', 'instance_type', 'addresses',
                  '_url')
