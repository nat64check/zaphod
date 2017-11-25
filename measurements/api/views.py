from django.db.models.query_utils import Q
from rest_framework import viewsets

from measurements.api.permissions import OwnerBasedPermission, CreatePublicBasedPermission
from measurements.api.serializers import ScheduleSerializer, TestRunSerializer, CreateTestRunSerializer, \
    CreatePublicTestRunSerializer, InstanceRunSerializer
from measurements.models import Schedule, TestRun, InstanceRun


class ScheduleViewSet(viewsets.ModelViewSet):
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

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

    def get_queryset(self):
        if self.request.user.is_superuser:
            return Schedule.objects.all()
        else:
            return Schedule.objects.filter(owner=self.request.user).prefetch_related('trillians')

    def perform_destroy(self, instance):
        assert isinstance(instance, Schedule)
        if instance.testrun_set.exists():
            last_testrun_date = instance.testrun_set.order_by('-requested').values_list('requested', flat=True).first()
            instance.end = last_testrun_date.date()
            instance.save()
        else:
            instance.delete()


class TestRunViewSet(viewsets.ModelViewSet):
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

    def perform_create(self, serializer):
        if self.request.user.is_anonymous:
            serializer.save(owner=None, is_public=True)
        else:
            serializer.save(owner=self.request.user)

    def get_queryset(self):
        if self.request.user.is_anonymous:
            return TestRun.objects.filter(is_public=True)
        elif self.request.user.is_superuser:
            return TestRun.objects.all()
        else:
            return TestRun.objects.filter(Q(is_public=True) | Q(owner=self.request.user))


class InstanceRunViewSet(viewsets.ReadOnlyModelViewSet):
    """
    list:
    Retrieve a list of instance runs.

    retrieve:
    Retrieve the details of a single instance run.
    """
    permission_classes = (OwnerBasedPermission,)
    serializer_class = InstanceRunSerializer

    def get_queryset(self):
        if self.request.user.is_anonymous:
            return InstanceRun.objects.filter(testrun__is_public=True)
        elif self.request.user.is_superuser:
            return InstanceRun.objects.all()
        else:
            return InstanceRun.objects.filter(Q(testrun__is_public=True) | Q(testrun__owner=self.request.user))
