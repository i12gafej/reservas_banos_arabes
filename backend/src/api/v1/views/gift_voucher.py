from rest_framework import status, viewsets
from rest_framework.response import Response

from api.v1.serializers.gift_voucher import GiftVoucherSerializer
from reservations.managers.gift_voucher import GiftVoucherManager  # asegúrate de implementarlo


class GiftVoucherViewSet(viewsets.ViewSet):
    """CRUD endpoints para cheques regalo."""

    def list(self, request):
        vouchers = GiftVoucherManager.list_vouchers()
        serializer = GiftVoucherSerializer(vouchers, many=True)
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
