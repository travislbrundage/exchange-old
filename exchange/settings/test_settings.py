import os

from default import *

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STATIC_ROOT = os.path.join(BASE_DIR, '../.storage/static_root')
MEDIA_ROOT = os.path.join(BASE_DIR, '../.storage/media')

# ensures tests are run on writing to file
AUDIT_TO_FILE = True

FILESERVICE_CONFIG = {
    'store_dir': os.path.join(MEDIA_ROOT, 'fileservice'),
    'types_allowed': ['.jpg', '.jpeg', '.png'],
    'streaming_supported': True
}

SECRET_KEY = os.getenv('SECRET_KEY', 'unit tests only not for production')
DEBUG = True
ALLOWED_HOSTS = ['testserver']
_INSTALLED_APPS = (
    'geonode',
    'exchange.core',
    'exchange.themes',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
)
#TEMPLATES = [
#    {
#        'BACKEND': 'django.template.backends.django.DjangoTemplates',
#        'DIRS': [],
#        'APP_DIRS': True,
#        'OPTIONS': {
#            'context_processors': [
#                'django.template.context_processors.debug',
#                'django.template.context_processors.request',
#                'django.contrib.auth.context_processors.auth',
#                'django.contrib.messages.context_processors.messages',
#            ],
#        },
#    },
#]
#DATABASES = {
#    'default': {
#        'ENGINE': 'django.db.backends.sqlite3',
#        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
#    }
#}


# DATABASES['exchange_imports'] = dj_database_url.parse(
#     'sqlite://'+os.path.join(BASE_DIR, 'imports_db.sqlite3')
# )

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_L10N = True
USE_TZ = True
STATIC_ROOT = os.path.join(BASE_DIR, '../.storage/static_root')
STATIC_URL = '/static/'
MEDIA_ROOT = os.path.join(BASE_DIR, '../.storage/media')
MEDIA_URL = '/media/'


GEOQUERY_ENABLED=True
SOCIAL_BUTTONS=True
STORYSCAPES_ENABLED=True
ES_SEARCH=True
ENABLE_SOCIAL_LOGIN=True
GEOQUERY_URL='http://www.example.com'
NOMINATIM_ENABLED=False
