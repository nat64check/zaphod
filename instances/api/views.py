from rest_framework import viewsets

from instances.api.filters import TrillianFilter, MarvinFilter
from instances.api.serializers import TrillianSerializer, MarvinSerializer
from instances.models import Trillian, Marvin


class TrillianViewSet(viewsets.ReadOnlyModelViewSet):
    """
    list:
    Retrieve a list of Trillians.

    retrieve:
    Retrieve the details of a single Trillian.
    """
    queryset = Trillian.objects.all().prefetch_related('marvins')
    serializer_class = TrillianSerializer
    filter_class = TrillianFilter

class MarvinViewSet(viewsets.ReadOnlyModelViewSet):
    """
    list:
    Retrieve a list of Marvins.
    Whenever a Marvin is updated a new object will be created so that old tests can keep referring to the Marvin
    as it was when running the test. Therefore multiple Marvins with the same name can appear in the list.

    retrieve:
    Retrieve the details of a single Marvin.
    """
    queryset = Marvin.objects.all().prefetch_related('trillian')
    serializer_class = MarvinSerializer
    filter_class = MarvinFilter
