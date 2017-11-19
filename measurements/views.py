from django.db.models.query_utils import Q
from rest_framework import viewsets

from measurements.models import Schedule, TestRun
from measurements.permissions import OwnerOrPublicBasedPermission, OwnerBasedPermission
from measurements.serializers import ScheduleSerializer, TestRunSerializer


class ScheduleViewSet(viewsets.ModelViewSet):
    """
    list:
    Retrieve a list of scheduled recurring tests.

    retrieve:
    Retrieve the details of a single schedule.

    create:
    Schedule a new recurring test.

    delete:
    Remove a scheduled recurring test.
    This is only possible if no tests have been run yet. If tests have already been run because of this schedule then
    the schedule will not be deleted but the end date will automatically be set to that of the last test run.

    partial_update:
    Change one or more settings of a scheduled recurring test.

    update:
    Update all the settings of a scheduled recurring test.
    """
    permission_classes = (OwnerBasedPermission,)
    serializer_class = ScheduleSerializer

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

    def get_queryset(self):
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
    permission_classes = (OwnerOrPublicBasedPermission,)
    serializer_class = TestRunSerializer

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

    def get_queryset(self):
        if self.request.user.is_anonymous:
            return TestRun.objects.filter(is_public=True)
        else:
            return TestRun.objects.filter(Q(is_public=True) | Q(owner=self.request.user))
