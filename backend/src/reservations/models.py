from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
import random

class Admin(models.Model):
    name = models.CharField(max_length=255, verbose_name="Nombre")
    surname = models.CharField(max_length=255, verbose_name="Apellidos")
    phone_number = models.CharField(max_length=50, null=True, blank=True, verbose_name="Teléfono")
    email = models.EmailField(unique=True, verbose_name="Email")
    password = models.TextField(verbose_name="Contraseña")
    created_at = models.DateTimeField(default=timezone.now, verbose_name="Fecha de creación")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Fecha de actualización")

    class Meta:
        verbose_name = "Administrador"
        verbose_name_plural = "Administradores"

class Agent(models.Model):
    name = models.CharField(max_length=255, verbose_name="Nombre")
    platform = models.CharField(max_length=100, null=True, blank=True, verbose_name="Plataforma")
    description = models.TextField(null=True, blank=True, verbose_name="Descripción")

    class Meta:
        verbose_name = "Agente"
        verbose_name_plural = "Agentes"

class Client(models.Model):
    name = models.CharField(max_length=255, verbose_name="Nombre")
    surname = models.CharField(max_length=255, null=True, blank=True, verbose_name="Apellidos")
    phone_number = models.CharField(max_length=50, null=True, blank=True, verbose_name="Teléfono")
    email = models.EmailField(null=True, blank=True, verbose_name="Email")
    created_at = models.DateTimeField(default=timezone.now, verbose_name="Fecha de registro")

    class Meta:
        verbose_name = "Cliente"
        verbose_name_plural = "Clientes"

    def __str__(self):
        return f"{self.name} {self.surname}"

class GiftVoucher(models.Model):
    code = models.CharField(max_length=255, unique=True, verbose_name="Código")
    bought_date = models.DateTimeField(default=timezone.now, verbose_name="Fecha de compra")
    price = models.DecimalField(max_digits=8, decimal_places=2, verbose_name="Precio")
    used = models.BooleanField(default=False, verbose_name="Usado")
    recipients_email = models.CharField(max_length=255, null=True, blank=True, verbose_name="Email del destinatario")
    recipients_name = models.CharField(max_length=255, null=True, blank=True, verbose_name="Nombre del destinatario")
    recipients_surname = models.CharField(max_length=255, null=True, blank=True, verbose_name="Apellidos del destinatario")
    gift_name = models.CharField(max_length=255, null=True, blank=True, verbose_name="Nombre del regalo")
    gift_description = models.TextField(null=True, blank=True, verbose_name="Descripción del regalo")
    buyer_client = models.ForeignKey(Client, on_delete=models.CASCADE, verbose_name="Cliente comprador")
    created_at = models.DateTimeField(default=timezone.now, verbose_name="Fecha de creación")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Fecha de actualización")
    product = models.ForeignKey('Product', on_delete=models.PROTECT, verbose_name="Producto", default=1)

    class Meta:
        verbose_name = "Cheque regalo"
        verbose_name_plural = "Cheques regalo"

class Product(models.Model):
    name = models.CharField(max_length=255, verbose_name="Nombre")
    observation = models.TextField(null=True, blank=True, verbose_name="Observaciones")
    description = models.TextField(null=True, blank=True, verbose_name="Descripción")
    price = models.DecimalField(max_digits=8, decimal_places=2, verbose_name="Precio")
    uses_capacity = models.BooleanField(default=True, verbose_name="Usa capacidad")
    uses_massagist = models.BooleanField(default=False, verbose_name="Requiere masajista")
    created_at = models.DateTimeField(default=timezone.now, verbose_name="Fecha de creación")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Fecha de actualización")
    visible = models.BooleanField(default=True, verbose_name="Visible")

    class Meta:
        verbose_name = "Producto"
        verbose_name_plural = "Productos"

    def __str__(self):
        return f"{self.name} (€{self.price})"

class BathType(models.Model):
    MASSAGE_TYPE_CHOICES = [
        ('relax', 'Relajante'),
        ('rock', 'Piedras'),
        ('exfoliation', 'Exfoliante'),
        ('none', 'Ninguno'),
    ]
    MASSAGE_DURATION_CHOICES = [
        ('15', '15 minutos'),
        ('30', '30 minutos'),
        ('60', '60 minutos'),
        ('0', 'Sin masaje'),
    ]
    name = models.CharField(max_length=255, verbose_name="Nombre")
    massage_type = models.CharField(max_length=50, choices=MASSAGE_TYPE_CHOICES, verbose_name="Tipo de masaje")
    massage_duration = models.CharField(max_length=50, choices=MASSAGE_DURATION_CHOICES, verbose_name="Duración del masaje")
    baths_duration = models.TimeField(default='02:00:00', verbose_name="Duración del baño")
    description = models.TextField(null=True, blank=True, verbose_name="Descripción")
    price = models.DecimalField(default=0.00, max_digits=8, decimal_places=2, verbose_name="Precio")

    class Meta:
        verbose_name = "Tipo de Baño"
        verbose_name_plural = "Tipos de Baños"

    def __str__(self):
        return self.name

class HostingType(models.Model):
    name = models.CharField(max_length=255, verbose_name="Nombre")
    capacity = models.IntegerField(verbose_name="Personas")
    description = models.TextField(null=True, blank=True, verbose_name="Descripción")

    class Meta:
        verbose_name = "Tipo de Alojamiento"
        verbose_name_plural = "Tipos de Alojamiento"

    def __str__(self):
        return f"{self.name} ({self.capacity} personas)"

class ProductBaths(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='baths', verbose_name="Producto")
    bath_type = models.ForeignKey(BathType, on_delete=models.PROTECT, verbose_name="Tipo de baño")
    quantity = models.IntegerField(default=1, verbose_name="Cantidad")

    class Meta:
        unique_together = ['product', 'bath_type']
        verbose_name = "Baño en Producto"
        verbose_name_plural = "Baños en Productos"

    def __str__(self):
        return f"{self.bath_type.name} (x{self.quantity})"

class ProductHosting(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='hostings', verbose_name="Producto")
    hosting_type = models.ForeignKey(HostingType, on_delete=models.PROTECT, verbose_name="Tipo de alojamiento")
    quantity = models.IntegerField(default=1, verbose_name="Cantidad")

    class Meta:
        unique_together = ['product', 'hosting_type']
        verbose_name = "Alojamiento en Producto"
        verbose_name_plural = "Alojamientos en Productos"

    def __str__(self):
        return f"{self.hosting_type.name} (x{self.quantity})"

class Availability(models.Model):
    TYPE_CHOICES = [
        ('weekday', 'Día de la semana'),
        ('punctual', 'Día específico'),
    ]
    WEEKDAY_CHOICES = [
        (1, 'Lunes'),
        (2, 'Martes'),
        (3, 'Miércoles'),
        (4, 'Jueves'),
        (5, 'Viernes'),
        (6, 'Sábado'),
        (7, 'Domingo'),
    ]
    type = models.CharField(max_length=20, choices=TYPE_CHOICES, verbose_name="Tipo")
    punctual_day = models.DateField(null=True, blank=True, verbose_name="Día específico")
    weekday = models.IntegerField(null=True, blank=True, choices=WEEKDAY_CHOICES, verbose_name="Día de la semana")
    created_at = models.DateTimeField(default=timezone.now, verbose_name="Fecha de creación")

    class Meta:
        verbose_name = "Disponibilidad"
        verbose_name_plural = "Disponibilidades"

    def __str__(self):
        if self.type == 'weekday':
            return f"Disponibilidad: {dict(self.WEEKDAY_CHOICES)[self.weekday]}"
        return f"Disponibilidad: {self.punctual_day}"

class AvailabilityRange(models.Model):
    initial_time = models.TimeField(verbose_name="Hora inicial")
    end_time = models.TimeField(verbose_name="Hora final")
    massagists_availability = models.IntegerField(verbose_name="Masajistas disponibles")
    availability = models.ForeignKey(Availability, on_delete=models.CASCADE, verbose_name="Disponibilidad")

    class Meta:
        verbose_name = "Disponibilidad por rango horario"
        verbose_name_plural = "Disponibilidades por rango horario"

class Book(models.Model):
    internal_order_id = models.CharField(max_length=255, unique=True, editable=False, verbose_name="ID de pedido")
    book_date = models.DateField(verbose_name="Fecha de reserva")
    hour = models.TimeField(verbose_name="Hora de la reserva")
    people = models.IntegerField(default=1, verbose_name="Nº personas")
    comment = models.TextField(null=True, blank=True, verbose_name="Comentarios")
    amount_paid = models.DecimalField(max_digits=8, decimal_places=2, verbose_name="Cantidad pagada")
    amount_pending = models.DecimalField(max_digits=8, decimal_places=2, verbose_name="Cantidad pendiente")
    payment_date = models.DateTimeField(null=True, blank=True, verbose_name="Fecha de pago")
    checked_in = models.BooleanField(default=False, verbose_name="Registrado")
    checked_out = models.BooleanField(default=False, verbose_name="Finalizado")
    created_at = models.DateTimeField(default=timezone.now, verbose_name="Fecha de creación")
    client = models.ForeignKey(Client, on_delete=models.CASCADE, verbose_name="Cliente")
    product = models.ForeignKey('Product', on_delete=models.PROTECT, verbose_name="Producto", default=1)
    
    # Campos para el creador genérico
    creator_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, null=True, blank=True, verbose_name="Origen de creación")
    creator_id = models.PositiveIntegerField(null=True, blank=True, verbose_name="ID del creador")
    creator = GenericForeignKey('creator_type', 'creator_id')

    class Meta:
        verbose_name = "Reserva"
        verbose_name_plural = "Reservas"

    def clean(self):
        from django.core.exceptions import ValidationError
        
        # Validar que el creator_type sea uno de los 4 tipos permitidos
        if self.creator_type:
            allowed_models = ['admin', 'agent', 'giftvoucher', 'webbooking']
            if self.creator_type.model not in allowed_models:
                raise ValidationError({
                    'creator_type': f'El origen de creación debe ser uno de: Administrador, Agente, Cheque regalo o Reserva web. Recibido: {self.creator_type.model}'
                })
        
        super().clean()

    def save(self, *args, **kwargs):
        if not self.internal_order_id:
            today = timezone.now().strftime('%d%m%Y')
            random_digits = ''.join([str(random.randint(0, 9)) for _ in range(4)])
            new_id = f"{today}{random_digits}"
            # Garantizar unicidad
            while Book.objects.filter(internal_order_id=new_id).exists():
                random_digits = ''.join([str(random.randint(0, 9)) for _ in range(4)])
                new_id = f"{today}{random_digits}"
            self.internal_order_id = new_id
        if not self.hour:
            self.hour = timezone.now().time()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Reserva {self.internal_order_id}"

    @property
    def creator_type_name(self):
        if not self.creator:
            return "Sin creador"
        if isinstance(self.creator, Admin):
            return "Administrador"
        elif isinstance(self.creator, Agent):
            return "Agente"
        elif isinstance(self.creator, GiftVoucher):
            return "Cheque regalo"
        elif isinstance(self.creator, WebBooking):
            return "Reserva web"
        return "Desconocido"

class WebBooking(models.Model):
    book = models.ForeignKey(Book, on_delete=models.CASCADE, verbose_name="Reserva")
    created_at = models.DateTimeField(default=timezone.now, verbose_name="Fecha de creación")

    class Meta:
        verbose_name = "Reserva Web"
        verbose_name_plural = "Reservas Web"

class Capacity(models.Model):
    """Modelo independiente para almacenar valores de aforo."""

    value = models.PositiveIntegerField(verbose_name="Aforo", default=8)

    # ――― Patrón singleton ―――
    def save(self, *args, **kwargs):
        if not self.pk and Capacity.objects.exists():
            raise ValueError("Ya existe un registro de aforo. Edítelo en lugar de crear otro.")
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = "Aforo"
        verbose_name_plural = "Aforo (único)"

    def __str__(self):
        return str(self.value)

