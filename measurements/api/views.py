from django.db.models.query_utils import Q
from rest_framework.mixins import UpdateModelMixin
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet
from rest_framework_serializer_extensions.views import SerializerExtensionsAPIViewMixin

from measurements.api.permissions import CreatePublicBasedPermission, InstanceRunPermission, OwnerBasedPermission, \
    OwnerOrPublicBasedPermission
from measurements.api.serializers import (CreatePublicTestRunSerializer, CreateTestRunSerializer,
                                          InstanceRunMessageSerializer, InstanceRunResultSerializer,
                                          InstanceRunSerializer, ScheduleSerializer, TestRunSerializer)
from measurements.models import InstanceRun, InstanceRunResult, Schedule, TestRun


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

    def get_queryset(self):
        if self.request.user.is_superuser:
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

    def get_serializer_class(self):
        if not self.request:
            # Docs get the serializer without having a request
            return TestRunSerializer

        if self.request.method == 'POST' and not self.request.user.is_superuser:
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

    def get_queryset(self):
        if self.request.user.is_anonymous:
            return TestRun.objects.filter(is_public=True)
        elif self.request.user.is_superuser:
            return TestRun.objects.all()
        else:
            return TestRun.objects.filter(Q(is_public=True) | Q(owner=self.request.user))


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

    def get_queryset(self):
        if self.request.user.is_superuser or self.request.user.has_perm('measurements.report_back'):
            return InstanceRun.objects.all()
        elif self.request.user.is_anonymous:
            return InstanceRun.objects.filter(testrun__is_public=True)
        else:
            return InstanceRun.objects.filter(Q(testrun__is_public=True) | Q(testrun__owner=self.request.user))

    def get_extensions_mixin_context(self):
        context = super().get_extensions_mixin_context()

        if self.request.user.has_perm('measurements.report_back'):
            # Trillians get the expanded view by default
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

    def get_queryset(self):
        if self.request.user.is_anonymous:
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

    def get_queryset(self):
        if self.request.user.is_anonymous:
            return InstanceRunResult.objects.filter(instancerun__testrun__is_public=True)
        elif self.request.user.is_superuser:
            return InstanceRunResult.objects.all()
        else:
            return InstanceRunResult.objects.filter(Q(instancerun__testrun__is_public=True) |
                                                    Q(instancerun__testrun__owner=self.request.user))
