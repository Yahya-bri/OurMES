from django.contrib.auth.models import AbstractUser
from django.db import models

class CustomUser(AbstractUser):
    # Add any additional fields you want for your user model
    pass

# In the future, you can add methods for authentication, token generation, etc.