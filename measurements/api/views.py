# ••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••
#  Copyright (c) 2018, S.J.M. Steffann. This software is licensed under the BSD 3-Clause License. Please seel the LICENSE file in the project root directory.
# ••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••

from django.db.models import Avg
from django.db.models.query_utils import Q
from rest_framework.mixins import UpdateModelMixin
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet
from rest_framework_serializer_extensions.views import SerializerExtensionsAPIViewMixin

from instances.models import instance_type_choices
from measurements.api.filters import ScheduleFilter, TestRunFilter, score_types
from measurements.api.permissions import (CreatePublicBasedPermission, InstanceRunPermission, OwnerBasedPermission,
                                          OwnerOrPublicBasedPermission)
from measurements.api.serializers import (CreatePublicTestRunSerializer, CreateTestRunSerializer,
                                          InstanceRunMessageSerializer, InstanceRunResultSerializer,
                                          InstanceRunSerializer, ScheduleSerializer, TestRunAverageSerializer,
                                          TestRunMessageSerializer, TestRunSerializer)
from measurements.models import (InstanceRun, InstanceRunMessage, InstanceRunResult, Schedule, TestRun, TestRunAverage,
                                 TestRunMessage)


class ScheduleViewSet(SerializerExtensionsAPIViewMixin, ModelViewSet):
    """
    list:
    Retrieve a list of scheduled recurring tests.

    retrieve:
    Retrieve the details of a single schedule.

    create:
    Schedule a new recurring test.

    delete:
    Remove a schedule.
    This is only possible if no tests have been run yet. If tests have already been run because of this schedule then
    the schedule will not be deleted but the end date will automatically be set to that of the last test run.

    partial_update:
    Change one or more settings of a schedule.

    update:
    Update all the settings of a schedule.
    """
    permission_classes = (OwnerBasedPermission,)
    serializer_class = ScheduleSerializer
    filter_class = ScheduleFilter
    ordering_fields = ('id', 'name', 'start', 'end')
    ordering = ('start',)

    def get_queryset(self):
        if not self.request:
            # Docs get the queryset without having a request
            return Schedule.objects.none()
        elif self.request.user.is_superuser:
            return Schedule.objects.all()
        else:
            return Schedule.objects.filter(owner=self.request.user)

    def perform_destroy(self, instance: Schedule):
        if instance.testruns.exists():
            last_testrun_date = instance.testruns.order_by('-requested').values_list('requested', flat=True).first()
            instance.end = last_testrun_date.date()
            instance.save()
        else:
            instance.delete()


class TestRunViewSet(SerializerExtensionsAPIViewMixin, ModelViewSet):
    """
    list:
    Retrieve a list of test runs.

    retrieve:
    Retrieve the details of a single test run.

    create:
    Request a new test run.

    delete:
    Remove a test run.

    partial_update:
    Change one or more settings of a test run.

    update:
    Update all the settings of a test run.
    """
    permission_classes = (CreatePublicBasedPermission,)
    filter_class = TestRunFilter
    ordering = ('requested',)

    def get_serializer_class(self):
        if not self.request:
            # Docs get the serializer without having a request
            return TestRunSerializer

        elif self.request.method == 'POST':
            # Special create serializers except for superusers, they can create anything
            if self.request.user.is_anonymous:
                # Anonymous users can only create public tests
                return CreatePublicTestRunSerializer
            else:
                # The rest may create private ones
                return CreateTestRunSerializer
        else:
            # Exposing all attributes when not creating
            return TestRunSerializer

    @property
    def ordering_fields(self):
        fields = ['id', 'requested',
                  'started', 'finished', 'analysed',
                  'image_score', 'resource_score', 'overall_score']

        for instance_type in instance_type_choices:
            for score_type in score_types:
                field_name = str(instance_type[0]).replace('-', '_') + '_' + str(score_type[0])
                fields.append(field_name)

        return fields

    def get_queryset(self):
        annotations = {}
        for instance_type in instance_type_choices:
            for score_type in score_types:
                field_name = str(instance_type[0]) + '_' + str(score_type[0])
                annotations[field_name] = Avg(
                    'averages__{}'.format(score_type[0].replace('-', '_')),
                    filter=Q(averages__instance_type=instance_type[0])
                )

        annotated = TestRun.objects.annotate(**annotations)

        if not self.request:
            # Docs get the queryset without having a request
            return annotated.none()
        elif self.request.user.is_anonymous:
            return annotated.filter(is_public=True)
        elif self.request.user.is_superuser:
            return annotated.all()
        else:
            return annotated.filter(Q(is_public=True) | Q(owner=self.request.user))


class TestRunMessageViewSet(SerializerExtensionsAPIViewMixin, ReadOnlyModelViewSet):
    """
    list:
    Retrieve a list of testrun messages.

    retrieve:
    Retrieve the details of a single testrun message.
    """
    permission_classes = (OwnerOrPublicBasedPermission,)
    serializer_class = TestRunMessageSerializer
    filter_fields = {
        'testrun': ['exact'],
        'severity': ['gte', 'lte', 'exact'],
        'message': ['icontains'],
    }
    ordering_fields = ('id', 'severity')
    ordering = ('id',)

    def get_queryset(self):
        if not self.request:
            # Docs get the queryset without having a request
            return TestRunMessage.objects.none()
        elif self.request.user.is_anonymous:
            return TestRunMessage.objects.filter(testrun__is_public=True)
        elif self.request.user.is_superuser:
            return TestRunMessage.objects.all()
        else:
            return TestRunMessage.objects.filter(Q(testrun__is_public=True) |
                                                 Q(testrun__owner=self.request.user))


class TestRunAverageViewSet(SerializerExtensionsAPIViewMixin, ReadOnlyModelViewSet):
    """
    list:
    Retrieve a list of testrun averages.

    retrieve:
    Retrieve the details of a single testrun average.
    """
    permission_classes = (OwnerOrPublicBasedPermission,)
    serializer_class = TestRunAverageSerializer
    filter_fields = {
        'testrun': ['exact'],
        'instance_type': ['exact'],
        'image_score': ['gt', 'gte', 'lt', 'lte', 'exact'],
        'resource_score': ['gt', 'gte', 'lt', 'lte', 'exact'],
        'overall_score': ['gt', 'gte', 'lt', 'lte', 'exact'],
    }
    ordering_fields = ('id', 'instance_type')
    ordering = ('testrun', 'instance_type')

    def get_queryset(self):
        if not self.request:
            # Docs get the queryset without having a request
            return TestRunAverage.objects.none()
        elif self.request.user.is_anonymous:
            return TestRunAverage.objects.filter(testrun__is_public=True)
        elif self.request.user.is_superuser:
            return TestRunAverage.objects.all()
        else:
            return TestRunAverage.objects.filter(Q(testrun__is_public=True) |
                                                 Q(testrun__owner=self.request.user))


class InstanceRunViewSet(SerializerExtensionsAPIViewMixin, ReadOnlyModelViewSet, UpdateModelMixin):
    """
    list:
    Retrieve a list of instance runs.

    retrieve:
    Retrieve the details of a single instance run.

    update:
    Update all the properties of an instance run.

    partial_update:
    Change one or more properties of an instance run.
    """
    permission_classes = (InstanceRunPermission,)
    serializer_class = InstanceRunSerializer
    filter_fields = {
        'testrun': ['exact'],
        'trillian': ['exact'],
        'testrun__owner': ['exact'],
        'testrun__url': ['exact', 'icontains'],
        'testrun__is_public': ['exact'],
        'started': ['gte', 'lte', 'isnull'],
        'finished': ['gte', 'lte', 'isnull'],
        'analysed': ['gte', 'lte', 'isnull'],
        'image_score': ['gte', 'lte'],
        'resource_score': ['gte', 'lte'],
        'overall_score': ['gte', 'lte'],
    }
    ordering_fields = ('id', 'started', 'finished', 'analysed', 'image_score', 'resource_score', 'overall_score')
    ordering = ('started', 'id')

    def get_queryset(self):
        if not self.request:
            # Docs get the queryset without having a request
            return InstanceRun.objects.none()
        elif self.request.user.is_superuser or self.request.user.has_perm('measurements.report_back'):
            return InstanceRun.objects.all()
        elif self.request.user.is_anonymous:
            return InstanceRun.objects.filter(testrun__is_public=True)
        else:
            return InstanceRun.objects.filter(Q(testrun__is_public=True) | Q(testrun__owner=self.request.user))

    def get_extensions_mixin_context(self):
        context = super().get_extensions_mixin_context()
        if not self.request:
            return context

        if self.request.user.has_perm('measurements.report_back') and not self.request.user.is_superuser:
            # Trillians get the expanded view by default, but save superusers from overload
            expand = context.setdefault('expand', set())
            expand.add('messages')
            expand.add('results__marvin')

        return context


class InstanceRunResultViewSet(SerializerExtensionsAPIViewMixin, ReadOnlyModelViewSet):
    """
    list:
    Retrieve a list of instance run results.

    retrieve:
    Retrieve the details of a single instance run result.
    """
    permission_classes = (OwnerOrPublicBasedPermission,)
    serializer_class = InstanceRunResultSerializer
    filter_fields = {
        'instancerun': ['exact'],
        'marvin': ['exact'],
        'when': ['gte', 'lte'],
    }
    ordering_fields = ('id', 'when', 'instancerun__started', 'instancerun__finished', 'instancerun__analysed')
    ordering = ('instancerun__started', 'id')

    def get_queryset(self):
        if not self.request:
            # Docs get the queryset without having a request
            return InstanceRunResult.objects.none()
        elif self.request.user.is_anonymous:
            return InstanceRunResult.objects.filter(instancerun__testrun__is_public=True)
        elif self.request.user.is_superuser:
            return InstanceRunResult.objects.all()
        else:
            return InstanceRunResult.objects.filter(Q(instancerun__testrun__is_public=True) |
                                                    Q(instancerun__testrun__owner=self.request.user))


class InstanceRunMessageViewSet(SerializerExtensionsAPIViewMixin, ReadOnlyModelViewSet):
    """
    list:
    Retrieve a list of instance run messages.

    retrieve:
    Retrieve the details of a single instance run message.
    """
    permission_classes = (OwnerOrPublicBasedPermission,)
    serializer_class = InstanceRunMessageSerializer
    filter_fields = {
        'instancerun': ['exact'],
        'severity': ['gte', 'lte', 'exact'],
        'message': ['icontains'],
    }
    ordering_fields = ('id', 'severity')
    ordering = ('id',)

    def get_queryset(self):
        if not self.request:
            # Docs get the queryset without having a request
            return InstanceRunMessage.objects.none()
        elif self.request.user.is_anonymous:
            return InstanceRunMessage.objects.filter(instancerun__testrun__is_public=True)
        elif self.request.user.is_superuser:
            return InstanceRunMessage.objects.all()
        else:
            return InstanceRunMessage.objects.filter(Q(instancerun__testrun__is_public=True) |
                                                     Q(instancerun__testrun__owner=self.request.user))
