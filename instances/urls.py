# ••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••
#  Copyright (c) 2018, S.J.M. Steffann. This software is licensed under the BSD
#  3-Clause License. Please see the LICENSE file in the project root directory.
# ••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••

from django.conf.urls import include, url
from rest_framework import routers

from instances.api.views import MarvinViewSet, TrillianViewSet

# Routers provide an easy way of automatically determining the URL conf.
instances_router = routers.SimpleRouter()
instances_router.register('trillians', TrillianViewSet, base_name='trillian')
instances_router.register('marvins', MarvinViewSet, base_name='marvin')

# Wire up our API using automatic URL routing.
urlpatterns = [
    url(r'^', include(instances_router.urls)),
]
