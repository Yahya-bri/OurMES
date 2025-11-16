from ..domain.models import Delivery


class DeliveryService:
    """Encapsulates delivery orchestration logic."""

    @staticmethod
    def create_delivery(**data) -> Delivery:
        return Delivery.objects.create(**data)

    @staticmethod
    def update_delivery(instance: Delivery, **data) -> Delivery:
        for attr, value in data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance

    @staticmethod
    def delete_delivery(instance: Delivery) -> None:
        instance.delete()
