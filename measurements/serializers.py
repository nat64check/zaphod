from rest_framework import serializers

from measurements.models import Schedule, TestRun


class ScheduleSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Schedule
        fields = ('id', 'owner_id', 'owner', 'name', 'url', 'time', 'start', 'end', 'frequency', 'is_public', '_url')
        # 'trillians',


class TestRunSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = TestRun
        fields = ('id', 'owner_id', 'schedule_id', 'schedule',
                  'url', 'requested', 'started', 'finished', 'is_public',
                  'image_score', 'image_feedback',
                  'resource_score', 'resource_feedback',
                  'overall_score', 'overall_feedback',
                  '_url')
