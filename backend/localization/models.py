from django.db import models

class Localization(models.Model):
    language_code = models.CharField(max_length=10)
    translation_key = models.CharField(max_length=255)
    translation_value = models.TextField()

    class Meta:
        unique_together = ('language_code', 'translation_key')

    def __str__(self):
        return f"{self.translation_key} in {self.language_code}"