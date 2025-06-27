from rest_framework import status, viewsets
from rest_framework.response import Response
from rest_framework.decorators import action

from api.v1.serializers.client import ClientSerializer
from reservations.managers.client import ClientManager


class ClientViewSet(viewsets.ViewSet):
    """Endpoints CRUD para clientes usando DTO/Manager."""

    def list(self, request):
        dtos = ClientManager.list_clients()
        serializer = ClientSerializer(dtos, many=True)
        return Response(serializer.data)

    def create(self, request):
        serializer = ClientSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        dto_created = serializer.save()
        return Response(ClientSerializer(dto_created).data, status=status.HTTP_201_CREATED)

    def retrieve(self, request, pk=None):
        # Reutilizar manager list + filter para simplicidad
        dto = next((c for c in ClientManager.list_clients() if str(c.id) == str(pk)), None)
        if dto is None:
            return Response(status=status.HTTP_404_NOT_FOUND)
        return Response(ClientSerializer(dto).data)

    def update(self, request, pk=None):
        dto_current = next((c for c in ClientManager.list_clients() if str(c.id) == str(pk)), None)
        if dto_current is None:
            return Response(status=status.HTTP_404_NOT_FOUND)
        serializer = ClientSerializer(dto_current, data=request.data)
        serializer.is_valid(raise_exception=True)
        dto_updated = serializer.save()
        return Response(ClientSerializer(dto_updated).data)

    def destroy(self, request, pk=None):
        ClientManager.delete_client(int(pk))
        return Response(status=status.HTTP_204_NO_CONTENT)

    # ------------------------------------------------------------------
    # Endpoints para unificación de clientes
    # ------------------------------------------------------------------

    @action(detail=False, methods=["get"], url_path="duplicados-preview")
    def preview_duplicates(self, request):
        """
        Obtiene una vista previa de los clientes duplicados sin realizar cambios.
        
        GET /api/v1/clientes/duplicados-preview/
        """
        try:
            preview_data = ClientManager.get_duplicate_clients_preview()
            return Response(preview_data)
        except Exception as e:
            return Response(
                {"detail": f"Error obteniendo vista previa de duplicados: {str(e)}"}, 
                status=status.HTTP_400_BAD_REQUEST
            )

    @action(detail=False, methods=["post"], url_path="unificar")
    def unify_clients(self, request):
        """
        Unifica todos los clientes duplicados encontrados en el sistema.
        
        POST /api/v1/clientes/unificar/
        """
        try:
            result = ClientManager.unify_duplicate_clients()
            return Response(result, status=status.HTTP_200_OK)
        except Exception as e:
            return Response(
                {"detail": f"Error durante la unificación de clientes: {str(e)}"}, 
                status=status.HTTP_400_BAD_REQUEST
            )

    @action(detail=False, methods=["get"], url_path="buscar-similares")
    def find_similar_clients(self, request):
        """
        Busca clientes similares basándose en criterios de búsqueda.
        
        GET /api/v1/clientes/buscar-similares/?name=X&surname=Y&email=Z&phone_number=W
        """
        try:
            name = request.query_params.get('name')
            surname = request.query_params.get('surname') 
            email = request.query_params.get('email')
            phone_number = request.query_params.get('phone_number')
            
            dtos = ClientManager.find_similar_clients(
                name=name,
                surname=surname,
                email=email,
                phone_number=phone_number
            )
            
            serializer = ClientSerializer(dtos, many=True)
            return Response(serializer.data)
            
        except Exception as e:
            return Response(
                {"detail": f"Error buscando clientes similares: {str(e)}"}, 
                status=status.HTTP_400_BAD_REQUEST
            ) 

    # ------------------------------------------------------------------
    # Endpoints para unificación de clientes
    # ------------------------------------------------------------------

    @action(detail=False, methods=["get"], url_path="duplicados-preview")
    def preview_duplicates(self, request):
        """
        Obtiene una vista previa de los clientes duplicados sin realizar cambios.
        
        GET /api/v1/clientes/duplicados-preview/
        """
        try:
            preview_data = ClientManager.get_duplicate_clients_preview()
            return Response(preview_data)
        except Exception as e:
            return Response(
                {"detail": f"Error obteniendo vista previa de duplicados: {str(e)}"}, 
                status=status.HTTP_400_BAD_REQUEST
            )

    @action(detail=False, methods=["post"], url_path="unificar")
    def unify_clients(self, request):
        """
        Unifica todos los clientes duplicados encontrados en el sistema.
        
        POST /api/v1/clientes/unificar/
        """
        try:
            result = ClientManager.unify_duplicate_clients()
            return Response(result, status=status.HTTP_200_OK)
        except Exception as e:
            return Response(
                {"detail": f"Error durante la unificación de clientes: {str(e)}"}, 
                status=status.HTTP_400_BAD_REQUEST
            )

    @action(detail=False, methods=["get"], url_path="buscar-similares")
    def find_similar_clients(self, request):
        """
        Busca clientes similares basándose en criterios de búsqueda.
        
        GET /api/v1/clientes/buscar-similares/?name=X&surname=Y&email=Z&phone_number=W
        """
        try:
            name = request.query_params.get('name')
            surname = request.query_params.get('surname') 
            email = request.query_params.get('email')
            phone_number = request.query_params.get('phone_number')
            
            dtos = ClientManager.find_similar_clients(
                name=name,
                surname=surname,
                email=email,
                phone_number=phone_number
            )
            
            serializer = ClientSerializer(dtos, many=True)
            return Response(serializer.data)
            
        except Exception as e:
            return Response(
                {"detail": f"Error buscando clientes similares: {str(e)}"}, 
                status=status.HTTP_400_BAD_REQUEST
            ) 