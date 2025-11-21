from django.db import models
from mes.plugins.basic.domain.models import Workstation


class MaintenanceLog(models.Model):
    TYPE_CHOICES = [
        ('preventive', 'Preventive'),
        ('corrective', 'Corrective'),
        ('breakdown', 'Breakdown'),
    ]

    workstation = models.ForeignKey(
        Workstation, on_delete=models.CASCADE, related_name='maintenance_logs')
    type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    description = models.TextField()
    start_time = models.DateTimeField()
    end_time = models.DateTimeField(null=True, blank=True)
    technician_name = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.workstation.name} - {self.type} ({self.start_time.date()})"

    @property
    def duration_hours(self):
        if self.end_time and self.start_time:
            diff = self.end_time - self.start_time
            return round(diff.total_seconds() / 3600, 2)
        return 0
