from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
from .models import (
    Admin, Agent, Client, GiftVoucher,
    Product, BathType, HostingType, Availability, AvailabilityRange, Capacity,
    Book, ProductBaths, ProductHosting,
    WebBooking
)
from django.db import models
from django import forms
from django.utils import timezone
from datetime import datetime
from django.contrib.contenttypes.models import ContentType

# ============================================================================
# CONFIGURACIÓN BÁSICA - TIPOS REUTILIZABLES
# ============================================================================

@admin.register(BathType)
class BathTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'massage_type', 'massage_duration', 'baths_duration', 'description', 'price')
    list_filter = ('massage_type', 'massage_duration', 'price')
    search_fields = ('name', 'description')
    ordering = ('name',)

@admin.register(HostingType)
class HostingTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'capacity', 'description')
    list_filter = ('capacity',)
    search_fields = ('name', 'description')
    ordering = ('name',)

# ============================================================================
# PRODUCTOS - INTERFAZ PRINCIPAL DE NEGOCIO
# ============================================================================

class ProductBathsInline(admin.TabularInline):
    model = ProductBaths
    extra = 1
    verbose_name = "Tipo de Baño"
    verbose_name_plural = "Tipos de Baños"
    autocomplete_fields = ['bath_type']

class ProductHostingInline(admin.TabularInline):
    model = ProductHosting
    extra = 1
    verbose_name = "Tipo de Alojamiento"
    verbose_name_plural = "Tipos de Alojamiento"
    autocomplete_fields = ['hosting_type']

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'baths_summary', 'hostings_summary', 'visible', 'uses_capacity', 'uses_massagist', 'created_at')
    list_filter = ('uses_capacity', 'uses_massagist', 'created_at')
    search_fields = ('name', 'description', 'observation')
    readonly_fields = ('created_at', 'updated_at')
    inlines = [ProductBathsInline, ProductHostingInline]
    ordering = ('-created_at',)

    def baths_summary(self, obj):
        baths = obj.baths.all()
        if not baths:
            return "Sin baños"
        return ", ".join([f"{bath.bath_type.name} (x{bath.quantity})" for bath in baths])
    baths_summary.short_description = "Baños incluidos"

    def hostings_summary(self, obj):
        hostings = obj.hostings.all()
        if not hostings:
            return "Sin alojamiento"
        return ", ".join([f"{hosting.hosting_type.name} (x{hosting.quantity})" for hosting in hostings])
    hostings_summary.short_description = "Alojamientos incluidos"

    fieldsets = (
        ('Información Básica', {
            'fields': ('name', 'description', 'observation', 'price')
        }),
        ('Configuración', {
            'fields': ('uses_capacity', 'uses_massagist', 'visible')
        }),
        ('Fechas', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

# ============================================================================
# RESERVAS - INTERFAZ PRINCIPAL DE NEGOCIO
# ============================================================================

# Widget personalizado para el selector de origen de creación
class CreatorTypeSelect(forms.Select):
    def __init__(self, attrs=None):
        choices = [
            ('', '---------'),  # Opción vacía
        ]
        
        # Obtener los ContentTypes específicos
        admin_ct = ContentType.objects.get_for_model(Admin)
        agent_ct = ContentType.objects.get_for_model(Agent)
        webbooking_ct = ContentType.objects.get_for_model(WebBooking)
        giftvoucher_ct = ContentType.objects.get_for_model(GiftVoucher)
        
        # Añadir las opciones con nombres personalizados
        choices.extend([
            (admin_ct.id, 'Administrador'),
            (agent_ct.id, 'Agente'),
            (webbooking_ct.id, 'Reserva Web'),
            (giftvoucher_ct.id, 'Cheque regalo'),
        ])
        
        super().__init__(attrs, choices)

    def render(self, name, value, attrs=None, renderer=None):
        # Asegurar que el valor sea un entero para la comparación
        if value:
            try:
                value = int(value)
            except (ValueError, TypeError):
                value = None
        
        return super().render(name, value, attrs, renderer) 



# Widget personalizado para horas cada 30 minutos entre 10:00 y 22:00
class HalfHourTimeSelect(forms.Select):
    def __init__(self, attrs=None):
        choices = []
        for hour in range(10, 23+1):
            for minute in (0, 30):
                time_str = f"{hour:02d}:{minute:02d}:00"
                label = f"{hour:02d}:{minute:02d}"
                choices.append((time_str, label))
        for hour in range(0, 1+1):
            for minute in (0, 30):
                time_str = f"{hour:02d}:{minute:02d}:00"
                label = f"{hour:02d}:{minute:02d}"
                choices.append((time_str, label))
        choices.append(('02:00:00', '02:00'))
        super().__init__(attrs, choices)

class CreatorTypeField(forms.ModelChoiceField):
    def __init__(self, *args, **kwargs):
        # Obtener los ContentTypes específicos
        allowed_models = [Admin, Agent, WebBooking, GiftVoucher]
        content_types = ContentType.objects.filter(
            model__in=[model._meta.model_name for model in allowed_models]
        )
        
        super().__init__(
            queryset=content_types,
            empty_label="---------",
            *args, **kwargs
        )

    def label_from_instance(self, obj):
        model_names = {
            'admin': 'Administrador',
            'agent': 'Agente',
            'webbooking': 'Reserva Web',
            'giftvoucher': 'Cheque regalo'
        }
        return model_names.get(obj.model, obj.model)

class CreatorModelField(forms.ModelChoiceField):
    def __init__(self, *args, **kwargs):
        super().__init__(
            queryset=Admin.objects.none(),  # Inicialmente vacío
            empty_label="---------",
            required=False,
            *args, **kwargs
        )

    def label_from_instance(self, obj):
        if isinstance(obj, Admin):
            return f"{obj.name} {obj.surname}"
        elif isinstance(obj, Agent):
            return obj.name
        elif isinstance(obj, GiftVoucher):
            return f"Vale #{obj.code} - {obj.gift_name}"
        elif isinstance(obj, WebBooking):
            return f"Reserva web #{obj.id}"
        return str(obj)

class BookForm(forms.ModelForm):
    booking_date = forms.DateField(
        label="Fecha de la reserva",
        widget=forms.DateInput(attrs={'type': 'date'})
    )
    booking_time = forms.TimeField(
        label="Hora de la reserva",
        widget=HalfHourTimeSelect()
    )

    class Meta:
        model = Book
        fields = '__all__'
        widgets = {
            'hour': HalfHourTimeSelect(attrs={'disabled': True}),
        }
        exclude = ['book_date']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        instance = kwargs.get('instance')
        initial = kwargs.get('initial', {})
        
        # Configurar fechas iniciales si hay instancia
        if instance:
            # `book_date` es ahora DateField y `hour` es TimeField separados
            self.initial.setdefault('booking_date', instance.book_date)
            self.initial.setdefault('booking_time', instance.hour)

        # Configurar campos del creador
        if 'creator_type' in self.fields:
            # Filtrar los tipos permitidos
            allowed_models = [Admin, Agent, WebBooking, GiftVoucher]
            content_types = ContentType.objects.filter(
                model__in=[model._meta.model_name for model in allowed_models]
            )
            self.fields['creator_type'].queryset = content_types
            self.fields['creator_type'].label = "Origen de creación"

        if 'creator_id' in self.fields:
            self.fields['creator_id'].label = "Creador"
            if instance and instance.creator_type:
                model_class = instance.creator_type.model_class()
                objects = model_class.objects.all()
                self.fields['creator_id'].queryset = objects
                
                # Personalizar la representación según el tipo
                if model_class == Admin:
                    self.fields['creator_id'].label_from_instance = lambda obj: f"{obj.name} {obj.surname}"
                elif model_class == Agent:
                    self.fields['creator_id'].label_from_instance = lambda obj: obj.name
                elif model_class == GiftVoucher:
                    self.fields['creator_id'].label_from_instance = lambda obj: f"Cheque #{obj.code} - {obj.gift_name}"
                elif model_class == WebBooking:
                    self.fields['creator_id'].label_from_instance = lambda obj: f"Reserva web #{obj.id}"
            else:
                self.fields['creator_id'].queryset = Admin.objects.none()

        if 'internal_order_id' in self.fields:
            self.fields['internal_order_id'].widget = forms.HiddenInput()
        if 'hour' in self.fields:
            self.fields['hour'].disabled = True

    def clean(self):
        cleaned_data = super().clean()
        booking_date = cleaned_data.get('booking_date')
        booking_time = cleaned_data.get('booking_time')

        # Ajustar los valores a los campos reales del modelo
        if booking_date:
            cleaned_data['book_date'] = booking_date
        if booking_time:
            cleaned_data['hour'] = booking_time

        return cleaned_data

    def save(self, commit=True):
        instance = super().save(commit=False)
        
        # Guardar fecha y hora independientes
        if self.cleaned_data.get('booking_date') is not None:
            instance.book_date = self.cleaned_data['booking_date']
        if self.cleaned_data.get('booking_time') is not None:
            instance.hour = self.cleaned_data['booking_time']
        
        if commit:
            instance.save()
        return instance

@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    form = BookForm
    list_display = ('internal_order_id', 'status_display', 'product_summary', 'created_at_display', 'client_name', 'client_phone', 'client_email', 'total_amount', 'people', 'booking_date_display', 'booking_time_display')
    list_filter = ('checked_in', 'checked_out', 'book_date', 'creator_type', 'created_at')
    search_fields = ('internal_order_id', 'client__name', 'client__surname', 'comment')
    readonly_fields = ('created_at', 'creator_type_display', 'internal_order_id', 'hour')
    ordering = ('-created_at',)
    autocomplete_fields = ['client']

    def created_at_display(self, obj):
        return obj.created_at.strftime('%d/%m/%Y - %H:%M')
    created_at_display.short_description = "Fecha de creación"
    created_at_display.admin_order_field = 'created_at'

    def client_name(self, obj):
        return f"{obj.client.name} {obj.client.surname or ''}"
    client_name.short_description = "Comprador"

    def client_phone(self, obj):
        return obj.client.phone_number or "No especificado"
    client_phone.short_description = "Teléfono"

    def client_email(self, obj):
        return obj.client.email or "No especificado"
    client_email.short_description = "Email"

    def total_amount(self, obj):
        total = obj.amount_paid + obj.amount_pending
        return f"€{total}"
    total_amount.short_description = "Precio"

    def product_summary(self, obj):
        return obj.product.name
    product_summary.short_description = "Producto"

    def booking_date_display(self, obj):
        return obj.book_date.strftime('%d/%m/%Y')
    booking_date_display.short_description = "Fecha reserva"

    def booking_time_display(self, obj):
        return obj.hour.strftime('%H:%M')
    booking_time_display.short_description = "Hora reserva"

    def creator_type_display(self, obj):
        return obj.creator_type_name
    creator_type_display.short_description = "Creado por"

    def status_display(self, obj):
        if obj.checked_out:
            return format_html('<span style="color: green;">✓ Finalizada</span>')
        elif obj.checked_in:
            return format_html('<span style="color: orange;">✓ Registrada</span>')
        else:
            return format_html('<span style="color: red;">⏳ Pendiente</span>')
    status_display.short_description = "Estado"

    fieldsets = (
        ('Información de la Reserva', {
            'fields': ('booking_date', 'booking_time', 'people', 'comment')
        }),
        ('Cliente', {
            'fields': ('client',)
        }),
        ('Pagos', {
            'fields': ('amount_paid', 'amount_pending', 'payment_date')
        }),
        ('Estado', {
            'fields': ('checked_in', 'checked_out')
        }),
        ('Creador', {
            'fields': ('creator_type', 'creator_id'),
            'classes': ('collapse',)
        }),
        ('Fechas', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )

# ============================================================================
# VALES REGALO - INTERFAZ DE NEGOCIO
# ============================================================================



class GiftVoucherForm(forms.ModelForm):
    class Meta:
        model = GiftVoucher
        fields = '__all__'
        widgets = {
            'hour': HalfHourTimeSelect(),
        }

@admin.register(GiftVoucher)
class GiftVoucherAdmin(admin.ModelAdmin):
    list_display = ('code', 'gift_name', 'buyer_info', 'recipient_info', 'price', 'used', 'created_at')
    list_filter = ('used', 'bought_date', 'created_at')
    search_fields = ('code', 'gift_name', 'buyer_client__name', 'recipients_name')
    readonly_fields = ('created_at', 'updated_at')
    ordering = ('-created_at',)
    autocomplete_fields = ['buyer_client']
    form = GiftVoucherForm

    def buyer_info(self, obj):
        return f"{obj.buyer_client.name} {obj.buyer_client.surname or ''}"
    buyer_info.short_description = "Comprador"

    def recipient_info(self, obj):
        if obj.recipients_name:
            return f"{obj.recipients_name} {obj.recipients_surname or ''}"
        return "No especificado"
    recipient_info.short_description = "Destinatario"

    fieldsets = (
        ('Información del Vale', {
            'fields': ('code', 'gift_name', 'gift_description', 'price')
        }),
        ('Comprador', {
            'fields': ('buyer_client', 'bought_date')
        }),
        ('Destinatario', {
            'fields': ('recipients_name', 'recipients_surname', 'recipients_email')
        }),
        ('Estado', {
            'fields': ('used',)
        }),
        ('Fechas', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

# ============================================================================
# GESTIÓN DE USUARIOS Y AGENTES
# ============================================================================

@admin.register(Admin)
class AdminAdmin(admin.ModelAdmin):
    list_display = ('name', 'surname', 'email', 'phone_number', 'created_at')
    search_fields = ('name', 'surname', 'email')
    readonly_fields = ('created_at', 'updated_at')
    ordering = ('name', 'surname')

@admin.register(Agent)
class AgentAdmin(admin.ModelAdmin):
    list_display = ('name', 'platform', 'description')
    list_filter = ('platform',)
    search_fields = ('name', 'description')
    ordering = ('name',)

@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ('name', 'surname', 'email', 'phone_number', 'created_at')
    search_fields = ('name', 'surname', 'email')
    readonly_fields = ('created_at',)
    ordering = ('name', 'surname')
    search_fields = ['name', 'surname', 'email', 'phone_number']  # Campos por los que se puede buscar

    def get_search_results(self, request, queryset, search_term):
        # Mejora la búsqueda para que busque en nombre y apellidos juntos
        queryset, use_distinct = super().get_search_results(request, queryset, search_term)
        if search_term:
            queryset |= self.model.objects.filter(
                models.Q(name__icontains=search_term) | 
                models.Q(surname__icontains=search_term) |
                models.Q(email__icontains=search_term) |
                models.Q(phone_number__icontains=search_term)
            )
        return queryset, use_distinct

# ============================================================================
# CONFIGURACIÓN TÉCNICA (OCULTA O MINIMIZADA)
# ============================================================================

@admin.register(WebBooking)
class WebBookingAdmin(admin.ModelAdmin):
    list_display = ('book', 'created_at')
    readonly_fields = ('created_at',)
    ordering = ('-created_at',)

@admin.register(ProductBaths)
class ProductBathsAdmin(admin.ModelAdmin):
    list_display = ('product', 'bath_type', 'quantity')
    list_filter = ('bath_type',)

@admin.register(ProductHosting)
class ProductHostingAdmin(admin.ModelAdmin):
    list_display = ('product', 'hosting_type', 'quantity')
    list_filter = ('hosting_type',)

@admin.register(Availability)
class AvailabilityAdmin(admin.ModelAdmin):
    list_display = ('type', 'punctual_day', 'weekday_display')
    list_filter = ('type', 'weekday')
    search_fields = ('type',)

    def weekday_display(self, obj):
        if obj.weekday:
            weekdays = dict(obj.WEEKDAY_CHOICES)
            return weekdays.get(obj.weekday, '')
        return ''
    weekday_display.short_description = "Día de la semana"



class AvailabilityRangeForm(forms.ModelForm):
    class Meta:
        model = AvailabilityRange
        fields = '__all__'
        widgets = {
            'initial_time': HalfHourTimeSelect(),
            'end_time': HalfHourTimeSelect(),
        }

@admin.register(AvailabilityRange)
class AvailabilityRangeAdmin(admin.ModelAdmin):
    list_display = ('availability', 'initial_time', 'end_time', 'massagists_availability')
    list_filter = ('availability',)
    search_fields = ('availability__type', 'initial_time', 'end_time')
    autocomplete_fields = ['availability']
    form = AvailabilityRangeForm 

@admin.register(Capacity)
class CapacityAdmin(admin.ModelAdmin):
    list_display = ('value',)

    def has_add_permission(self, request):
        # Permitir «Añadir» solo si no existe ningún registro
        return not Capacity.objects.exists()

