from django.utils import timezone
from rest_framework import serializers

from instances.api.serializers import NestedMarvinSerializer
from instances.models import Marvin
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
    marvin = NestedMarvinSerializer()

    class Meta:
        model = InstanceRunResult
        fields = ('marvin', 'instance_type', 'when', 'ping_response', 'web_response')


class InstanceRunSerializer(serializers.HyperlinkedModelSerializer):
    messages = NestedInstanceRunMessageSerializer(many=True, read_only=True)
    results = NestedInstanceRunResultsSerializer(many=True, required=False)

    class Meta:
        model = InstanceRun
        fields = ('id', 'testrun', 'testrun_id', 'trillian', 'trillian_id', 'trillian_url',
                  'requested', 'started', 'finished',
                  'dns_results',
                  'image_score', 'image_feedback',
                  'resource_score', 'resource_feedback',
                  'overall_score', 'overall_feedback',
                  'messages', 'results',
                  '_url')

        read_only_fields = ('testrun', 'trillian', 'trillian_url', 'requested',
                            'image_score', 'image_feedback',
                            'resource_score', 'resource_feedback',
                            'overall_score', 'overall_feedback',
                            'messages')

    def update(self, instance: InstanceRun, validated_data):
        # If marked as finished don't update anymore
        if instance.finished:
            return instance

        results = validated_data.pop('results', None)
        for result in results:
            try:
                marvin, new_marvin = Marvin.objects.update_or_create(
                    defaults=result['marvin'],
                    trillian=instance.trillian,
                    name=result['marvin']['name']
                )
            except KeyError:
                # We need marvin to be able to store data
                continue

            InstanceRunResult.objects.update_or_create(
                defaults={
                    'when': result.get('when', timezone.now()),
                    'ping_response': result.get('ping_response', {}),
                    'web_response': result.get('web_response', {}),
                },
                instancerun=instance,
                marvin=marvin
            )

        return super().update(instance, validated_data)
