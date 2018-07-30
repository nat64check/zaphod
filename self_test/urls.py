from django.conf.urls import url

from self_test.views import self_test

urlpatterns = [
    url(r'^$', self_test, name='self-test'),
]
