from rest_framework import serializers

from instances.models import Marvin, Trillian


class TrillianSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Trillian
        fields = ('id', 'name', 'admins',
                  'hostname', 'is_alive', 'version', 'country', 'location', 'marvins', 'marvin_ids',
                  'flag',
                  '_url')


class NestedMarvinSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Marvin
        fields = ('name', 'hostname', 'type', 'version',
                  'browser_name', 'browser_version', 'instance_type', 'addresses',
                  'first_seen', 'last_seen')


class MarvinSerializer(NestedMarvinSerializer):
    class Meta(NestedMarvinSerializer.Meta):
        fields = ('id', 'trillian', 'trillian_id') + NestedMarvinSerializer.Meta.fields + ('_url',)
