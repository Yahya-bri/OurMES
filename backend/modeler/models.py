from django.db import models

class Modeler(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

class AnotherModel(models.Model):
    modeler = models.ForeignKey(Modeler, related_name='another_models', on_delete=models.CASCADE)
    attribute = models.CharField(max_length=255)

    def __str__(self):
        return self.attribute