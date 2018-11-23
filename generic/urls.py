# ••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••
#  Copyright (c) 2018, S.J.M. Steffann. This software is licensed under the BSD
#  3-Clause License. Please see the LICENSE file in the project root directory.
# ••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••

from django.conf.urls import include, url
from rest_framework import routers

from generic.api.views import InfoViewSet, UserViewSet

# Routers provide an easy way of automatically determining the URL conf.
generic_router = routers.SimpleRouter()
generic_router.register('info', InfoViewSet, base_name='info')
generic_router.register('users', UserViewSet, base_name='user')

# Wire up our API using automatic URL routing.
urlpatterns = [
    url(r'^', include(generic_router.urls)),
]
