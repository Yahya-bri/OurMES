from django.db import models

class Delivery(models.Model):
    order_number = models.CharField(max_length=100)
    delivery_date = models.DateField()
    status = models.CharField(max_length=50)
    recipient_name = models.CharField(max_length=255)
    recipient_address = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Delivery {self.order_number} to {self.recipient_name}"