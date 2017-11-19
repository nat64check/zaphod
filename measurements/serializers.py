from rest_framework import serializers

from measurements.models import Schedule, TestRun, TestRunMessage


class ScheduleSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Schedule
        fields = ('id', 'owner', 'owner_id',
                  'name', 'url', 'time', 'start', 'end', 'frequency', 'is_public', 'trillians', 'trillian_ids',
                  '_url')
        read_only_fields = ('owner',)


class NestedTestRunMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = TestRunMessage
        fields = ('severity', 'message')


class TestRunSerializer(serializers.HyperlinkedModelSerializer):
    messages = NestedTestRunMessageSerializer(many=True, read_only=True)

    class Meta:
        model = TestRun
        fields = ('id', 'owner', 'schedule',
                  'url', 'requested', 'started', 'finished', 'is_public',
                  'image_score', 'image_feedback',
                  'resource_score', 'resource_feedback',
                  'overall_score', 'overall_feedback',
                  'messages',
                  '_url')
        read_only_fields = ('owner',)


class CreateTestRunSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = TestRun
        fields = ('id', 'url', 'is_public', '_url')


class CreatePublicTestRunSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = TestRun
        fields = ('id', 'url', '_url')
