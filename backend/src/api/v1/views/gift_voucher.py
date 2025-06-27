from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from api.v1.serializers.gift_voucher import GiftVoucherSerializer, GiftVoucherWithDetailsSerializer, StaffGiftVoucherSerializer
from reservations.managers.gift_voucher import GiftVoucherManager  # asegúrate de implementarlo


class GiftVoucherViewSet(viewsets.ViewSet):
    """CRUD endpoints para cheques regalo."""

    def list(self, request):
        vouchers = GiftVoucherManager.list_vouchers_with_details()
        serializer = GiftVoucherWithDetailsSerializer(vouchers, many=True)
        return Response(serializer.data)

    def create(self, request):
        serializer = GiftVoucherSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        dto_created = serializer.save()
        return Response(GiftVoucherSerializer(dto_created).data, status=status.HTTP_201_CREATED)

    def retrieve(self, request, pk=None):
        dto = GiftVoucherManager.get_voucher(int(pk))  # supposing this method
        if dto is None:
            return Response(status=status.HTTP_404_NOT_FOUND)
        return Response(GiftVoucherSerializer(dto).data)

    def update(self, request, pk=None):
        current = GiftVoucherManager.get_voucher(int(pk))
        if current is None:
            return Response(status=status.HTTP_404_NOT_FOUND)
        serializer = GiftVoucherSerializer(current, data=request.data)
        serializer.is_valid(raise_exception=True)
        dto_updated = serializer.save()
        return Response(GiftVoucherSerializer(dto_updated).data)

    def destroy(self, request, pk=None):
        GiftVoucherManager.delete_voucher(int(pk))
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, methods=['post'], url_path='create-from-staff')
    def create_from_staff(self, request):
        """Crear cheque regalo desde staff con masajes y datos completos."""
        serializer = StaffGiftVoucherSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        try:
            dto_created = serializer.save()
            return Response(GiftVoucherSerializer(dto_created).data, status=status.HTTP_201_CREATED)
        except ValueError as e:
            return Response(
                {'error': str(e)}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            return Response(
                {'error': f'Error interno del servidor: {str(e)}'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


    @action(detail=False, methods=['post'], url_path='create-from-staff')
    def create_from_staff(self, request):
        """Crear cheque regalo desde staff con masajes y datos completos."""
        serializer = StaffGiftVoucherSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        try:
            dto_created = serializer.save()
            return Response(GiftVoucherSerializer(dto_created).data, status=status.HTTP_201_CREATED)
        except ValueError as e:
            return Response(
                {'error': str(e)}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            return Response(
                {'error': f'Error interno del servidor: {str(e)}'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
