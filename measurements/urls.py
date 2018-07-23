from django.conf.urls import include, url
from rest_framework import routers

from measurements.api.views import InstanceRunResultViewSet, InstanceRunViewSet, ScheduleViewSet, TestRunViewSet

# Routers provide an easy way of automatically determining the URL conf.
measurements_router = routers.SimpleRouter()
measurements_router.register('schedules', ScheduleViewSet, base_name='schedule')
measurements_router.register('testruns', TestRunViewSet, base_name='testrun')
measurements_router.register('instanceruns', InstanceRunViewSet, base_name='instancerun')
measurements_router.register('instancerunresults', InstanceRunResultViewSet, base_name='instancerunresult')

# Wire up our API using automatic URL routing.
urlpatterns = [
    url(r'^', include(measurements_router.urls)),
]
