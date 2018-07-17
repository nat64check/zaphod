from django.db.models.query_utils import Q
from rest_framework import mixins, viewsets
from rest_framework_serializer_extensions.views import SerializerExtensionsAPIViewMixin

from measurements.api.permissions import CreatePublicBasedPermission, InstanceRunPermission, OwnerBasedPermission
from measurements.api.serializers import (CreatePublicTestRunSerializer, CreateTestRunSerializer, InstanceRunSerializer,
                                          ScheduleSerializer, TestRunSerializer)
from measurements.models import InstanceRun, Schedule, TestRun


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

    def perform_destroy(self, instance: Schedule):
        if instance.testruns.exists():
            last_testrun_date = instance.testruns.order_by('-requested').values_list('requested', flat=True).first()
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


class InstanceRunViewSet(SerializerExtensionsAPIViewMixin, viewsets.ReadOnlyModelViewSet, mixins.UpdateModelMixin):
    """
    list:
    Retrieve a list of instance runs.

    retrieve:
    Retrieve the details of a single instance run.
    """
    permission_classes = (InstanceRunPermission,)
    serializer_class = InstanceRunSerializer
    extensions_expand_id_only = {'messages', 'results'}
    extensions_exclude = {'results__id',
                          'results__instancerun',
                          'results__instancerun_id',
                          'results___url',
                          'results__marvin_id',
                          'results__marvin__id',
                          'results__marvin__trillian_id',
                          'results__marvin___url'}

    def get_extensions_mixin_context(self):
        context = super().get_extensions_mixin_context()
        if self.detail:
            context['expand'] = {'messages', 'results__marvin'}
        return context

    def get_queryset(self):
        if self.request.user.is_anonymous:
            return InstanceRun.objects.filter(testrun__is_public=True)
        elif self.request.user.is_superuser:
            return InstanceRun.objects.all()
        else:
            return InstanceRun.objects.filter(Q(testrun__is_public=True) | Q(testrun__owner=self.request.user))
