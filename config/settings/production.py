"""
Production settings for CRM Nutrición project.
"""

from .base import *

# Security settings for production
DEBUG = False
ALLOWED_HOSTS = get_env('ALLOWED_HOSTS', default='').split(',') if get_env('ALLOWED_HOSTS') else []

# Security middleware
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',  # For static files
] + MIDDLEWARE

# Database ya está configurada en base.py con get_env()
# Las variables se configuran en el servidor de producción

# Static files for production
COMPRESS_ENABLED = True
COMPRESS_OFFLINE = True
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# Security settings
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
SECURE_HSTS_SECONDS = 3600
X_FRAME_OPTIONS = 'DENY'

# HTTPS settings (habilitar cuando uses HTTPS)
SECURE_SSL_REDIRECT = get_env('SECURE_SSL_REDIRECT', default=False, cast=bool)
SESSION_COOKIE_SECURE = get_env('SESSION_COOKIE_SECURE', default=False, cast=bool)
CSRF_COOKIE_SECURE = get_env('CSRF_COOKIE_SECURE', default=False, cast=bool)

# Logging for production
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'file': {
            'level': 'ERROR',
            'class': 'logging.FileHandler',
            'filename': BASE_DIR / 'logs' / 'django.log',
            'formatter': 'verbose',
        },
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
    },
    'root': {
        'level': 'INFO',
        'handlers': ['console', 'file'],
    },
}
