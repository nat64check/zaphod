from rest_framework import viewsets

from instances.models import Trillian, Marvin
from instances.serializers import TrillianSerializer, MarvinSerializer


class TrillianViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Trillian.objects.all()
    serializer_class = TrillianSerializer


class MarvinViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Marvin.objects.all()
    serializer_class = MarvinSerializer
