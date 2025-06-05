"""
Development settings for CRM Nutrición project.
"""

from .base import *

# Debug mode enabled for development
DEBUG = True

# Allow all hosts in development
ALLOWED_HOSTS = ['localhost', '127.0.0.1', '[::1]']

# Development-specific apps
INSTALLED_APPS += [
    'django_extensions',
]

# Development middleware
MIDDLEWARE += [
    # Add any development-specific middleware here
]

# Database for development (uses .env variables)
# Already configured in base.py with decouple

# Email backend for development (console)
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# Static files for development
SASS_PROCESSOR_ENABLED = True
COMPRESS_ENABLED = False  # Disable compression in development

# Logging for development
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'INFO',
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': False,
        },
    },
}
