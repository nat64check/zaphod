from datetime import timedelta

from django.db.transaction import atomic
from django.utils import timezone
from django.utils.translation import gettext as _
from rest_framework.exceptions import ValidationError as RestValidationError
from rest_framework.fields import CurrentUserDefault, HiddenField
from rest_framework.relations import HyperlinkedRelatedField
from rest_framework.serializers import HyperlinkedModelSerializer
from rest_framework_serializer_extensions.serializers import SerializerExtensionsMixin

from instances.api.serializers import MarvinSerializer, TrillianSerializer
from instances.models import Marvin, Trillian
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


class CreatePublicTestRunSerializer(HyperlinkedModelSerializer):
    trillians = HyperlinkedRelatedField(view_name='trillian-detail',
                                        many=True,
                                        required=True,
                                        queryset=Trillian.objects.filter(is_alive=True))

    class Meta:
        model = TestRun
        fields = ('id', 'url', 'requested', 'trillians', '_url')

    def validate_requested(self, value):
        if value < timezone.now() - timedelta(minutes=1):
            raise RestValidationError(_('You cannot create tests in the past'))

        return value

    def validate_trillians(self, value):
        if not value:
            raise RestValidationError(_('You must specify at least one location to test from'))

        return value

    @atomic
    def create(self, validated_data):
        # Force public for anonymous tests
        owner = validated_data.get('owner', None)
        if not owner:
            validated_data['is_public'] = True

        # Get the list of trillians out before creating, that's a read-only property
        trillians = validated_data.pop('trillians', [])
        instance = super().create(validated_data)

        # Now create an instancerun for each trillian
        for trillian in trillians:
            InstanceRun.objects.create(
                testrun=instance,
                trillian=trillian,
            )

        return instance


class CreateTestRunSerializer(CreatePublicTestRunSerializer):
    owner = HiddenField(default=CurrentUserDefault())

    class Meta(CreatePublicTestRunSerializer.Meta):
        fields = list(CreatePublicTestRunSerializer.Meta.fields) + ['owner', 'is_public']


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
