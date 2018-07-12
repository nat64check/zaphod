"""zaphod_be URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URL conf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf import settings
from django.conf.urls import include, url
from django.contrib import admin
from django.views.generic.base import RedirectView
from rest_framework.documentation import include_docs_urls
from rest_framework.routers import DefaultRouter
from rest_framework_swagger.views import get_swagger_view

from generic.api.views import UserViewSet
from generic.views import reload_uwsgi
from instances.urls import instances_router
from measurements.urls import measurements_router

router = DefaultRouter()
router.register('users', UserViewSet, base_name='user')
router.registry.extend(measurements_router.registry)
router.registry.extend(instances_router.registry)

# TODO: Consider OTP for Admin site
# otp_admin_site = OTPAdminSite(OTPAdminSite.name)
# for model_cls, model_admin in admin.site._registry.items():
#     otp_admin_site.register(model_cls, model_admin.__class__)

urlpatterns = [
    url(r'^swagger/$', get_swagger_view(title='NAT64Check Zaphod API')),
    url(r'^docs/', include_docs_urls(title='NAT64Check Zaphod API')),

    url(r'^admin/reload/$', reload_uwsgi, name='reload_uwsgi'),

    # TODO: Consider OTP for Admin site
    # url(r'^admin/', otp_admin_site.urls),

    url(r'^admin/', admin.site.urls),
    url(r'^i18n/', include('django.conf.urls.i18n')),

    url(r'^api-auth/', include('rest_framework.urls')),
    url(r'^api/v1/', include(router.urls)),
    url(r'^api/$', RedirectView.as_view(url='v1')),

    url(r'^$', RedirectView.as_view(url='api/')),
]

if settings.DEBUG:
    import debug_toolbar
    from django.conf.urls.static import static

    urlpatterns = urlpatterns + [
        url(r'^__debug__/', include(debug_toolbar.urls)),
    ] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
