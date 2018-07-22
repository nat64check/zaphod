from django.utils import timezone
from rest_framework.serializers import HyperlinkedModelSerializer
from rest_framework_serializer_extensions.serializers import SerializerExtensionsMixin

from instances.api.serializers import MarvinSerializer, TrillianSerializer
from instances.models import Marvin
from measurements.models import InstanceRun, InstanceRunMessage, InstanceRunResult, Schedule, TestRun, TestRunMessage


class ScheduleSerializer(HyperlinkedModelSerializer):
    class Meta:
        model = Schedule
        fields = ('id', 'owner', 'owner_id',
                  'name', 'url', 'time', 'start', 'end', 'frequency', 'is_public',
                  'trillians', 'trillian_ids',
                  'testruns', 'testrun_ids',
                  '_url')
        read_only_fields = ('owner',)


class TestRunMessageSerializer(HyperlinkedModelSerializer):
    class Meta:
        model = TestRunMessage
        fields = ('severity', 'message')


class TestRunSerializer(HyperlinkedModelSerializer):
    messages = TestRunMessageSerializer(many=True, read_only=True)

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


class CreateTestRunSerializer(HyperlinkedModelSerializer):
    class Meta:
        model = TestRun
        fields = ('id', 'url', 'is_public', '_url')


class CreatePublicTestRunSerializer(HyperlinkedModelSerializer):
    class Meta:
        model = TestRun
        fields = ('id', 'url', '_url')


class InstanceRunMessageSerializer(HyperlinkedModelSerializer):
    class Meta:
        model = InstanceRunMessage
        fields = ('severity', 'message')


class InstanceRunResultsSerializer(SerializerExtensionsMixin, HyperlinkedModelSerializer):
    class Meta:
        model = InstanceRunResult
        fields = ('id', 'instancerun', 'instance_type', 'when', 'ping_response', 'web_response', '_url')
        expandable_fields = dict(
            marvin=MarvinSerializer,
            instancerun="measurements.api.serializers.InstanceRunSerializer",
        )


class InstanceRunSerializer(SerializerExtensionsMixin, HyperlinkedModelSerializer):
    class Meta:
        model = InstanceRun
        fields = ('id',
                  'trillian_url',
                  'requested', 'started', 'finished', 'analysed',
                  'dns_results',
                  'image_score', 'image_feedback',
                  'resource_score', 'resource_feedback',
                  'overall_score', 'overall_feedback',
                  '_url')

        read_only_fields = ('testrun',
                            'trillian', 'trillian_url', 'requested', 'analysed',
                            'image_score', 'image_feedback',
                            'resource_score', 'resource_feedback',
                            'overall_score', 'overall_feedback')

        expandable_fields = dict(
            testrun=TestRunSerializer,
            trillian=TrillianSerializer,
            results=dict(
                serializer=InstanceRunResultsSerializer,
                many=True,
            ),
            messages=dict(
                serializer=InstanceRunMessageSerializer,
                many=True,
            ),
        )

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

        messages = {(message['severity'], message['message'])
                    for message in validated_data.pop('messages', [])
                    if 'severity' in message and 'message' in message}
        existing_messages = {(message.severity, message.message)
                             for message in instance.messages.filter(source='T')}

        # Add new messages
        for severity, message in messages - existing_messages:
            InstanceRunMessage.objects.create(
                instancerun=instance,
                source='T',
                severity=severity,
                message=message
            )

        # Remove old messages
        for severity, message in existing_messages - messages:
            InstanceRunMessage.objects.filter(severity=severity, message=message).delete()

        return super().update(instance, validated_data)
