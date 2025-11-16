from django.db import models


class Mail(models.Model):
    subject = models.CharField(max_length=255)
    body = models.TextField()
    to_email = models.EmailField()
    status = models.CharField(max_length=32, default='pending')
    sent_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.subject} -> {self.to_email}"
