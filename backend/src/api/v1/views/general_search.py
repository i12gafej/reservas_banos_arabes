from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from reservations.services.general_search import GeneralSearchService


class GeneralSearchView(APIView):
    """Vista para realizar búsquedas generales en la base de datos."""
    
    def get(self, request):
        """
        Endpoint para búsqueda general.
        
        Query Parameters:
        - q: Término de búsqueda (requerido)
        - autocomplete_client: ID del cliente para autocompletar (opcional)
        """
        term = request.query_params.get('q', '').strip()
        autocomplete_client_id = request.query_params.get('autocomplete_client')
        
        # Si se solicita autocompletar datos de cliente
        if autocomplete_client_id:
            try:
                client_id = int(autocomplete_client_id)
                client_data = GeneralSearchService.get_client_data_for_autocomplete(client_id)
                if client_data:
                    return Response({
                        'success': True,
                        'client_data': client_data
                    })
                else:
                    return Response({
                        'success': False,
                        'error': 'Cliente no encontrado'
                    }, status=status.HTTP_404_NOT_FOUND)
            except ValueError:
                return Response({
                    'success': False,
                    'error': 'ID de cliente inválido'
                }, status=status.HTTP_400_BAD_REQUEST)
        
        # Validar término de búsqueda
        if not term:
            return Response({
                'success': False,
                'error': 'Término de búsqueda requerido'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        if len(term) < 2:
            return Response({
                'success': False,
                'error': 'El término de búsqueda debe tener al menos 2 caracteres'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            # Realizar búsqueda
            results = GeneralSearchService.search(term)
            
            # Calcular total de resultados
            total_results = sum(len(results[key]) for key in results)
            
            return Response({
                'success': True,
                'query': term,
                'total_results': total_results,
                'results': results
            })
            
        except Exception as e:
            return Response({
                'success': False,
                'error': f'Error interno del servidor: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
