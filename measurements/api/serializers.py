from rest_framework import serializers

from measurements.models import InstanceRun, InstanceRunMessage, InstanceRunResult, Schedule, TestRun, TestRunMessage


class ScheduleSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Schedule
        fields = ('id', 'owner', 'owner_id',
                  'name', 'url', 'time', 'start', 'end', 'frequency', 'is_public',
                  'trillians', 'trillian_ids',
                  'testruns', 'testrun_ids',
                  '_url')
        read_only_fields = ('owner',)


class NestedTestRunMessageSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = TestRunMessage
        fields = ('severity', 'message')


class TestRunSerializer(serializers.HyperlinkedModelSerializer):
    messages = NestedTestRunMessageSerializer(many=True, read_only=True)

    class Meta:
        model = TestRun
        fields = ('id', 'owner', 'owner_id', 'schedule', 'schedule_id',
                  'url', 'requested', 'started', 'finished', 'is_public',
                  'image_score', 'image_feedback',
                  'resource_score', 'resource_feedback',
                  'overall_score', 'overall_feedback',
                  'messages', 'instanceruns',
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


class NestedInstanceRunMessageSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = InstanceRunMessage
        fields = ('severity', 'message')


class NestedInstanceRunResultsSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = InstanceRunResult
        fields = ('marvin', 'marvin_id', 'instance_type', 'pings', 'web_response')


class InstanceRunSerializer(serializers.HyperlinkedModelSerializer):
    messages = NestedInstanceRunMessageSerializer(many=True, read_only=True)
    results = NestedInstanceRunResultsSerializer(many=True, read_only=True)

    class Meta:
        model = InstanceRun
        fields = ('id', 'testrun', 'testrun_id', 'trillian', 'trillian_id', 'id_on_trillian',
                  'requested', 'started', 'finished',
                  'dns_results',
                  'image_score', 'image_feedback',
                  'resource_score', 'resource_feedback',
                  'overall_score', 'overall_feedback',
                  'messages', 'results',
                  '_url')
