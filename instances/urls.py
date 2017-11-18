from django.conf.urls import url, include
from rest_framework import routers

from instances.views import TrillianViewSet, MarvinViewSet

# Routers provide an easy way of automatically determining the URL conf.
instances_router = routers.SimpleRouter()
instances_router.register('trillians', TrillianViewSet)
instances_router.register('marvins', MarvinViewSet)

# Wire up our API using automatic URL routing.
urlpatterns = [
    url(r'^', include(instances_router.urls)),
]
