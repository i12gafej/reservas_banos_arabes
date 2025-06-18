from typing import Optional
from django.db import transaction

from reservations.models import BathType, HostingType, Product, ProductBaths, ProductHosting
from reservations.dtos.product import BathTypeDTO, HostingTypeDTO, ProductCreateDTO, BathQuantityDTO, HostingQuantityDTO


class ProductManager:
    """Gestor de operaciones relacionadas con productos y sus componentes."""

    # ---------------------------------------------------------------------
    # Métodos de BathType
    # ---------------------------------------------------------------------

    @staticmethod
    def create_bath_type(dto: BathTypeDTO) -> BathType:
        """Crea y devuelve un BathType a partir del DTO (sin comprobar duplicados)."""
        return BathType.objects.create(
            name=dto.name,
            massage_type=dto.massage_type,
            massage_duration=dto.massage_duration,
            baths_duration=dto.baths_duration,
            description=dto.description or "",
        )

    @staticmethod
    def get_bath_type_if_exists(dto: BathTypeDTO) -> Optional[BathType]:
        """Devuelve el BathType existente que coincide con nombre + atributos, o None."""
        try:
            return BathType.objects.get(
                name=dto.name,
                massage_type=dto.massage_type,
                massage_duration=dto.massage_duration,
                baths_duration=dto.baths_duration,
            )
        except BathType.DoesNotExist:
            return None

    # ---------------------------------------------------------------------
    # Métodos de HostingType
    # ---------------------------------------------------------------------

    @staticmethod
    def create_hosting_type(dto: HostingTypeDTO) -> HostingType:
        """Crea y devuelve un HostingType a partir del DTO."""
        return HostingType.objects.create(
            name=dto.name,
            capacity=dto.capacity,
            description=dto.description or "",
        )

    @staticmethod
    def get_hosting_type_if_exists(dto: HostingTypeDTO) -> Optional[HostingType]:
        """Devuelve el HostingType existente (mismo nombre y capacidad) o None."""
        try:
            return HostingType.objects.get(
                name=dto.name,
                capacity=dto.capacity,
            )
        except HostingType.DoesNotExist:
            return None

    # ---------------------------------------------------------------------
    # CRUD de Producto
    # ---------------------------------------------------------------------

    @staticmethod
    @transaction.atomic
    def create_product(dto: ProductCreateDTO) -> Product:
        """Crea un producto junto a sus registros ProductBaths y ProductHosting."""

        dto.validate()

        product = Product.objects.create(
            name=dto.name,
            observation=dto.observation or "",
            description=dto.description or "",
            price=dto.price,
            uses_capacity=dto.uses_capacity,
            uses_massagist=dto.uses_massagist,
            visible=dto.visible,
        )

        # Procesar baños
        for bath_q in dto.baths:
            if bath_q.quantity <= 0:
                continue  # ignorar entradas sin cantidad

            bath_type_obj = None
            if bath_q.bath_type.id:
                bath_type_obj = BathType.objects.get(id=bath_q.bath_type.id)
            else:
                bath_type_obj = ProductManager.get_bath_type_if_exists(bath_q.bath_type)
                if bath_type_obj is None:
                    bath_type_obj = ProductManager.create_bath_type(bath_q.bath_type)

            ProductBaths.objects.create(
                product=product,
                bath_type=bath_type_obj,
                quantity=bath_q.quantity,
            )

        # Procesar alojamientos
        for host_q in dto.hostings:
            if host_q.quantity <= 0:
                continue

            hosting_type_obj = None
            if host_q.hosting_type.id:
                hosting_type_obj = HostingType.objects.get(id=host_q.hosting_type.id)
            else:
                hosting_type_obj = ProductManager.get_hosting_type_if_exists(host_q.hosting_type)
                if hosting_type_obj is None:
                    hosting_type_obj = ProductManager.create_hosting_type(host_q.hosting_type)

            ProductHosting.objects.create(
                product=product,
                hosting_type=hosting_type_obj,
                quantity=host_q.quantity,
            )

        return product

    @staticmethod
    def get_product_by_id(product_id: int) -> Product:
        """Devuelve el producto con sus relaciones prefetcheadas o lanza DoesNotExist."""
        return (
            Product.objects
            .prefetch_related("baths__bath_type", "hostings__hosting_type")
            .get(id=product_id)
        )

    @staticmethod
    @transaction.atomic
    def update_product(product_id: int, dto: ProductCreateDTO) -> Product:
        """Sobrescribe los datos y las relaciones de un producto existente."""

        product = ProductManager.get_product_by_id(product_id)

        # Actualizar campos básicos
        product.name = dto.name
        product.observation = dto.observation or ""
        product.description = dto.description or ""
        product.price = dto.price
        product.uses_capacity = dto.uses_capacity
        product.uses_massagist = dto.uses_massagist
        product.visible = dto.visible
        product.save()

        # Limpiar relaciones actuales
        ProductBaths.objects.filter(product=product).delete()
        ProductHosting.objects.filter(product=product).delete()

        # Volver a crearlas usando la misma lógica que en create
        ProductManager._create_related_records(product, dto)

        return product

    @staticmethod
    @transaction.atomic
    def delete_product(product_id: int) -> None:
        """Elimina un producto y sus relaciones."""
        Product.objects.filter(id=product_id).delete()

    # ------------------------------------------------------------------
    # Helper interno
    # ------------------------------------------------------------------

    @staticmethod
    def _create_related_records(product: Product, dto: ProductCreateDTO) -> None:
        """Factoriza la creación de ProductBaths y ProductHosting (usado en create y update)."""

        # Baños
        for bath_q in dto.baths:
            if bath_q.quantity <= 0:
                continue

            bath_type_obj = None
            if bath_q.bath_type.id:
                bath_type_obj = BathType.objects.get(id=bath_q.bath_type.id)
            else:
                bath_type_obj = ProductManager.get_bath_type_if_exists(bath_q.bath_type)
                if bath_type_obj is None:
                    bath_type_obj = ProductManager.create_bath_type(bath_q.bath_type)

            ProductBaths.objects.create(product=product, bath_type=bath_type_obj, quantity=bath_q.quantity)

        # Alojamientos
        for host_q in dto.hostings:
            if host_q.quantity <= 0:
                continue

            hosting_type_obj = None
            if host_q.hosting_type.id:
                hosting_type_obj = HostingType.objects.get(id=host_q.hosting_type.id)
            else:
                hosting_type_obj = ProductManager.get_hosting_type_if_exists(host_q.hosting_type)
                if hosting_type_obj is None:
                    hosting_type_obj = ProductManager.create_hosting_type(host_q.hosting_type)

            ProductHosting.objects.create(product=product, hosting_type=hosting_type_obj, quantity=host_q.quantity)
