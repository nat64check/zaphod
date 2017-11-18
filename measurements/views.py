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
    This is only possible if no tests have been run yet. If you want to stop a scheduled recurring test please set its
    end date.

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
        if self.request.user.is_anonymous:
            return Schedule.objects.none()
        else:
            return Schedule.objects.filter(owner=self.request.user)


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
