from rest_framework.permissions import AllowAny
from rest_framework.viewsets import ReadOnlyModelViewSet
from rest_framework_serializer_extensions.views import SerializerExtensionsAPIViewMixin

from instances.api.filters import MarvinFilter, TrillianFilter
from instances.api.serializers import MarvinSerializer, TrillianSerializer
from instances.models import Marvin, Trillian


class TrillianViewSet(SerializerExtensionsAPIViewMixin, ReadOnlyModelViewSet):
    """
    list:
    Retrieve a list of Trillians.

    retrieve:
    Retrieve the details of a single Trillian.
    """
    permission_classes = (AllowAny,)
    queryset = Trillian.objects.all()
    serializer_class = TrillianSerializer
    filter_class = TrillianFilter


class MarvinViewSet(SerializerExtensionsAPIViewMixin, ReadOnlyModelViewSet):
    """
    list:
    Retrieve a list of Marvins.
    Whenever a Marvin is updated a new object will be created so that old tests can keep referring to the Marvin
    as it was when running the test. Therefore multiple Marvins with the same name can appear in the list.

    retrieve:
    Retrieve the details of a single Marvin.
    """
    permission_classes = (AllowAny,)
    queryset = Marvin.objects.all()
    serializer_class = MarvinSerializer
    filter_class = MarvinFilter
