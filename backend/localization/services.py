from django.utils.translation import gettext as _
from .models import Localization

class LocalizationService:
    @staticmethod
    def get_localization_data(language_code):
        """
        Retrieve localization data for the specified language code.
        """
        return Localization.objects.filter(language_code=language_code).values()

    @staticmethod
    def create_localization_entry(language_code, key, value):
        """
        Create a new localization entry.
        """
        localization_entry = Localization(language_code=language_code, key=key, value=value)
        localization_entry.save()
        return localization_entry

    @staticmethod
    def update_localization_entry(entry_id, key, value):
        """
        Update an existing localization entry.
        """
        try:
            localization_entry = Localization.objects.get(id=entry_id)
            localization_entry.key = key
            localization_entry.value = value
            localization_entry.save()
            return localization_entry
        except Localization.DoesNotExist:
            return None

    @staticmethod
    def delete_localization_entry(entry_id):
        """
        Delete a localization entry.
        """
        try:
            localization_entry = Localization.objects.get(id=entry_id)
            localization_entry.delete()
            return True
        except Localization.DoesNotExist:
            return False