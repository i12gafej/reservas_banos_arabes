from rest_framework import status, viewsets
from rest_framework.response import Response
from rest_framework.decorators import action

from api.v1.serializers.book import BookingSerializer
from reservations.managers.book import BookManager
from reservations.dtos.book import StaffBathRequestDTO


class BookViewSet(viewsets.ViewSet):
    """CRUD endpoints para reservas (Book) usando DTO + manager."""

    def list(self, request):
        dtos = BookManager.list_bookings()
        serializer = BookingSerializer(dtos, many=True)
        return Response(serializer.data)

    def create(self, request):
        serializer = BookingSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        dto_created = serializer.save()
        return Response(BookingSerializer(dto_created).data, status=status.HTTP_201_CREATED)

    def retrieve(self, request, pk=None):
        dto = next((b for b in BookManager.list_bookings() if str(b.id) == str(pk)), None)
        if dto is None:
            return Response(status=status.HTTP_404_NOT_FOUND)
        return Response(BookingSerializer(dto).data)

    def update(self, request, pk=None):
        dto_current = next((b for b in BookManager.list_bookings() if str(b.id) == str(pk)), None)
        if dto_current is None:
            return Response(status=status.HTTP_404_NOT_FOUND)
        serializer = BookingSerializer(dto_current, data=request.data)
        serializer.is_valid(raise_exception=True)
        dto_updated = serializer.save()
        return Response(BookingSerializer(dto_updated).data)

    def destroy(self, request, pk=None):
        BookManager.delete_booking(int(pk))
        return Response(status=status.HTTP_204_NO_CONTENT)

    # ------------------------------------------------------------------
    # Endpoint específico para reservas desde staff
    # ------------------------------------------------------------------

    @action(detail=False, methods=["post"], url_path="staff")
    def create_from_staff(self, request):
        data = request.data

        try:
            baths = data.get("baths", [])
            bath_dtos = [StaffBathRequestDTO(**b) for b in data.get("baths", [])]

            dto_created = BookManager.create_booking_from_staff(
                name=data["name"],
                surname=data.get("surname", ""),
                phone=data["phone_number"],
                email=data.get("email", ""),
                date_str=data["date"],
                hour_str=data["hour"],
                people=data["people"],
                baths=bath_dtos,
                comment=data.get("comment", ""),
            )
            return Response(BookingSerializer(dto_created).data, status=status.HTTP_201_CREATED)
        except KeyError as e:
            return Response({"detail": f"Campo requerido faltante: {e.args[0]}"}, status=400)
