# ••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••
#  Copyright (c) 2018, S.J.M. Steffann. This software is licensed under the BSD 3-Clause License. Please seel the LICENSE file in the project root directory.
# ••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••

from datetime import timedelta

from django.db.transaction import atomic
from django.utils import timezone
from django.utils.translation import gettext as _
from rest_framework.exceptions import ValidationError as RestValidationError
from rest_framework.fields import CurrentUserDefault, FloatField, HiddenField
from rest_framework.relations import HyperlinkedRelatedField
from rest_framework.serializers import HyperlinkedModelSerializer
from rest_framework_serializer_extensions.serializers import SerializerExtensionsMixin

from generic.api.fields import SerializerExtensionsJSONField
from generic.api.serializers import UserSerializer
from generic.utils import print_warning
from instances.api.serializers import MarvinSerializer, TrillianSerializer
from instances.models import Marvin, Trillian, instance_type_choices
from measurements.api.filters import score_types
from measurements.models import (InstanceRun, InstanceRunMessage, InstanceRunResult, Schedule, TestRun, TestRunAverage,
                                 TestRunMessage)


class ScheduleSerializer(SerializerExtensionsMixin, HyperlinkedModelSerializer):
    owner = HiddenField(default=CurrentUserDefault())

    class Meta:
        model = Schedule
        fields = ('id', 'owner', 'owner_id',
                  'name', 'url', 'time', 'start', 'end', 'frequency', 'is_public', 'is_active',
                  'trillians', 'testruns',
                  '_url')
        read_only_fields = ('owner', 'testruns', 'is_active')
        expandable_fields = dict(
            owner=UserSerializer,
            trillians=dict(
                serializer='instances.api.serializers.TrillianSerializer',
                many=True,
            ),
            testruns=dict(
                serializer='measurements.api.serializers.TestRunSerializer',
                many=True,
            ),
        )


class TestRunSerializer(SerializerExtensionsMixin, HyperlinkedModelSerializer):
    trillians = HyperlinkedRelatedField(view_name='trillian-detail', many=True, read_only=True)
    messages = HyperlinkedRelatedField(view_name='testrunmessage-detail', many=True, read_only=True)
    instanceruns = HyperlinkedRelatedField(view_name='instancerun-detail', many=True, read_only=True)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for instance_type in instance_type_choices:
            for score_type in score_types:
                field_name = str(instance_type[0]).replace('-', '_') + '_' + str(score_type[0])
                self.fields[field_name] = FloatField(read_only=True)

    class Meta:
        model = TestRun
        fields = ('id', 'owner', 'owner_id', 'schedule', 'schedule_id',
                  'url', 'requested', 'started', 'finished', 'is_public',
                  'image_score', 'image_feedback',
                  'resource_score', 'resource_feedback',
                  'overall_score', 'overall_feedback',
                  'trillians', 'messages', 'instanceruns',
                  '_url')
        read_only_fields = ('owner',)
        expandable_fields = dict(
            owner=UserSerializer,
            trillians=dict(
                serializer='instances.api.serializers.TrillianSerializer',
                many=True,
            ),
            messages=dict(
                serializer='measurements.api.serializers.TestRunMessageSerializer',
                many=True,
            ),
            instanceruns=dict(
                serializer='measurements.api.serializers.InstanceRunSerializer',
                many=True,
            ),
        )


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


class TestRunMessageSerializer(HyperlinkedModelSerializer):
    class Meta:
        model = TestRunMessage
        fields = ('id', 'severity', 'message', '_url')


class TestRunAverageSerializer(HyperlinkedModelSerializer):
    class Meta:
        model = TestRunAverage
        fields = ('id', 'instance_type',
                  'image_score', 'resource_score', 'overall_score',
                  '_url')


class InstanceRunSerializer(SerializerExtensionsMixin, HyperlinkedModelSerializer):
    class Meta:
        model = InstanceRun
        fields = ('id',
                  'testrun', 'testrun_id', 'trillian', 'trillian_id', 'trillian_url',
                  'requested', 'started', 'finished', 'analysed',
                  'dns_results', 'results', 'messages',
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
                serializer='measurements.api.serializers.InstanceRunResultSerializer',
                many=True,
            ),
            messages=dict(
                serializer='measurements.api.serializers.InstanceRunMessageSerializer',
                many=True,
            ),
        )

    def update(self, instance: InstanceRun, validated_data):
        # If marked as finished don't update anymore
        if instance.finished:
            print_warning("Instance already finished, not updating")
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


class InstanceRunMessageSerializer(HyperlinkedModelSerializer):
    class Meta:
        model = InstanceRunMessage
        fields = ('id', 'severity', 'message', '_url')


class InstanceRunResultSerializer(SerializerExtensionsMixin, HyperlinkedModelSerializer):
    web_response = SerializerExtensionsJSONField()
    ping_response = SerializerExtensionsJSONField()

    class Meta:
        model = InstanceRunResult
        fields = ('id', 'marvin', 'marvin_id', 'instancerun', 'instancerun_id', 'instance_type',
                  'when', 'ping_response', 'web_response',
                  'image_score', 'image_feedback',
                  'resource_score', 'resource_feedback',
                  'overall_score', 'overall_feedback',
                  '_url')

        read_only_fields = ('instancerun',)

        expandable_fields = dict(
            marvin=MarvinSerializer,
            instancerun="measurements.api.serializers.InstanceRunSerializer",
        )
