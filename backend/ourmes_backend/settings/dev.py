from .base import *
import os

# Development overrides
DEBUG = True

ALLOWED_HOSTS = ['localhost', '127.0.0.1']

# Use SQLite by default for development
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}

# Optional: relaxed CORS in dev if corsheaders is enabled
CORS_ALLOW_ALL_ORIGINS = os.getenv('CORS_ALLOW_ALL_ORIGINS', 'True') == 'True'