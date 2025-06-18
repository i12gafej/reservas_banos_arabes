from rest_framework import viewsets
from rest_framework.response import Response
from .serializers import ExampleSerializer


class ExampleViewSet(viewsets.ViewSet):
    """Vista de ejemplo para comprobar la API v1"""

    def list(self, request):
        data = {'message': 'Hola desde API v1'}
        serializer = ExampleSerializer(data)
        return Response(serializer.data) 