from django.http import JsonResponse
from django.contrib.contenttypes.models import ContentType
from .models import Admin, Agent, WebBooking, GiftVoucher

def get_creators(request):
    creator_type_id = request.GET.get('creator_type')
    if not creator_type_id:
        return JsonResponse({'error': 'No creator type provided'}, status=400)

    try:
        content_type = ContentType.objects.get(id=creator_type_id)
        model_class = content_type.model_class()
        
        creators = []
        if model_class == Admin:
            creators = [{'id': obj.id, 'name': f"{obj.name} {obj.surname}"} for obj in model_class.objects.all()]
        elif model_class == Agent:
            creators = [{'id': obj.id, 'name': obj.name} for obj in model_class.objects.all()]
        elif model_class == GiftVoucher:
            creators = [{'id': obj.id, 'name': f"Cheque #{obj.code} - {obj.gift_name}"} for obj in model_class.objects.all()]
        elif model_class == WebBooking:
            creators = [{'id': obj.id, 'name': f"Reserva web #{obj.id}"} for obj in model_class.objects.all()]
        
        return JsonResponse(creators, safe=False)
    except ContentType.DoesNotExist:
        return JsonResponse({'error': 'Invalid creator type'}, status=400) 