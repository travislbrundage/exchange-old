# -*- coding: utf-8 -*-
#########################################################################
#
# Copyright (C) 2016 Boundless Spatial
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.
#
#########################################################################

import os
import dj_database_url
import copy
from ast import literal_eval as le
from geonode.settings import *  # noqa
from geonode.settings import (
    MIDDLEWARE_CLASSES,
    STATICFILES_DIRS,
    INSTALLED_APPS,
    CELERY_IMPORTS,
    MAP_BASELAYERS,
    DATABASES,
    CATALOGUE
)


def str2bool(v):
    if v and len(v) > 0:
        return v.lower() in ("yes", "true", "t", "1")
    else:
        return False


def isValid(v):
    if v and len(v) > 0:
        return True
    else:
        return False

SITENAME = os.getenv('SITENAME', 'exchange')
WSGI_APPLICATION = "exchange.wsgi.application"
ROOT_URLCONF = 'exchange.urls'
SOCIAL_BUTTONS = str2bool(os.getenv('SOCIAL_BUTTONS', 'False'))

USE_TZ = str2bool(os.getenv('USE_TZ', 'True'))

# Installation on a closed 'airgapped' network
DISABLE_BOUNDLESS_LINK_IN_FOOTER = str2bool(os.getenv(
    'DISABLE_BOUNDLESS_LINK_IN_FOOTER',
    'False')
)

# classification banner
CLASSIFICATION_BANNER_ENABLED = str2bool(os.getenv(
    'CLASSIFICATION_BANNER_ENABLED',
    'False')
)
CLASSIFICATION_TEXT = os.getenv('CLASSIFICATION_TEXT', 'UNCLASSIFIED//FOUO')
CLASSIFICATION_TEXT_COLOR = os.getenv('CLASSIFICATION_TEXT_COLOR', 'white')
CLASSIFICATION_BACKGROUND_COLOR = os.getenv(
    'CLASSIFICATION_BACKGROUND_COLOR',
    'green'
)
CLASSIFICATION_LINK = os.getenv('CLASSIFICATION_LINK', None)

# extent filter
EXTENT_FILTER_ENABLED = str2bool(os.getenv('EXTENT_FILTER_ENABLED', 'True'))

# login warning
LOGIN_WARNING_ENABLED = str2bool(os.getenv('LOGIN_WARNING_ENABLED', 'False'))

if LOGIN_WARNING_ENABLED:
    LOGIN_WARNING_TEXT = os.getenv('LOGIN_WARNING_TEXT', '''<p>You are accessing a U.S. Government (USG)
        Information System (IS) that is provided
        for USG-authorized use only.  By using this IS (which includes any device attached to this IS), you
        consent to the following conditions:</p><ul><li>The USG routinely intercepts, and monitors
        communications on this IS for purposes including, but not limited to, penetration testing,
        COMSEC monitoring, network operations and defense, personnel misconduct (PM), law enforcement
        (LE), and counterintelligence (CI) investigations.</li><li>At any time, the USG may inspect
        and seize data stored on this IS.</li><li>Communications using, or data stored on,
        this IS are not private, are subject to routine monitoring, interception, and search,
        and may be disclosed or used for any USG-authorized purpose.</li></ul><p>This IS includes security measures
        (e.g., authentication and access controls) to protect USG interests -- not for your personal
        benefit or privacy.  Notwithstanding the above, using this IS does not constitute consent to
        PM, LE, or CI investigative searching or monitoring of the content of privileged communications,
        or work product, related to personal representation or services by attorneys, psychotherapists,
        or clergy, and their assistants.  Such communications and work product are private and
        confidential.  See User Agreement for details.</p>''')

# registration
EMAIL_HOST = os.getenv('EMAIL_HOST', None)
EMAIL_PORT = le(os.getenv('EMAIL_PORT', '25'))
EMAIL_USE_TLS = str2bool(os.getenv('EMAIL_USE_TLS', 'False'))
EMAIL_BACKEND = os.getenv('EMAIL_BACKEND', 'django.core.mail.backends.smtp.EmailBackend')
EMAIL_HOST_USER = os.getenv('EMAIL_HOST_USER', None)
EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD', None)
DEFAULT_FROM_EMAIL = os.getenv('DEFAULT_FROM_EMAIL', None)
THEME_ACCOUNT_CONTACT_EMAIL = os.getenv('THEME_ACCOUNT_CONTACT_EMAIL', None)
ACCOUNT_ACTIVATION_DAYS = le(os.getenv('ACCOUNT_ACTIVATION_DAYS', '7'))

# path setup
LOCAL_ROOT = os.path.abspath(os.path.dirname(__file__))
APP_ROOT = os.path.join(LOCAL_ROOT, os.pardir)

# static files storage
STATICFILES_DIRS = [
    os.path.join(APP_ROOT, "static"),
    os.path.join(APP_ROOT, "thumbnails", "static"),
] + STATICFILES_DIRS

# template settings
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(APP_ROOT, 'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.contrib.auth.context_processors.auth',
                'django.core.context_processors.debug',
                'django.core.context_processors.i18n',
                'django.core.context_processors.tz',
                'django.core.context_processors.media',
                'django.core.context_processors.static',
                'django.core.context_processors.request',
                'django.contrib.messages.context_processors.messages',
                'account.context_processors.account',
                'geonode.context_processors.resource_urls',
                'geonode.geoserver.context_processors.geoserver_urls',
                'django_classification_banner.context_processors.'
                'classification',
                'exchange.core.context_processors.resource_variables',
            ],
            'debug': DEBUG,
        },
    },
]

# middleware
MIDDLEWARE_CLASSES = (
    'whitenoise.middleware.WhiteNoiseMiddleware',
) + MIDDLEWARE_CLASSES

ADDITIONAL_APPS = os.getenv(
    'ADDITIONAL_APPS',
    ()
)

if isinstance(ADDITIONAL_APPS, str):
    ADDITIONAL_APPS = tuple(map(str.strip, ADDITIONAL_APPS.split(',')))

OSGEO_IMPORTER_ENABLED = str2bool(os.getenv('OSGEO_IMPORTER_ENABLED', 'True'))
GEONODE_CLIENT_ENABLED = str2bool(os.getenv('GEONODE_CLIENT_ENABLED', 'True'))
STORYSCAPES_ENABLED = str2bool(os.getenv('STORYSCAPES_ENABLED', 'False'))

if STORYSCAPES_ENABLED:
    RESOURCE_PUBLISHING = True

# installed applications
INSTALLED_APPS = (
    'flat',
    'exchange.core',
    'exchange.themes',
    'exchange.fileservice',
    'exchange.thumbnails',
    'geonode',
    'geonode.contrib.geogig',
    'geonode.contrib.slack',
    'django_classification_banner',
    'maploom',
    'solo',
    'exchange-docs',
    'exchange.storyscapes',
    'composer',
    'social_django',
) + ADDITIONAL_APPS + INSTALLED_APPS

if OSGEO_IMPORTER_ENABLED:
    INSTALLED_APPS = ('osgeo_importer',) + INSTALLED_APPS
else:
    UPLOADER = {
        'BACKEND': 'geonode.importer',
        'OPTIONS': {
            'TIME_ENABLED': True,
            'MOSAIC_ENABLED': False,
        }
    }

if GEONODE_CLIENT_ENABLED:
    INSTALLED_APPS = ('geonode-client',) + INSTALLED_APPS
    LAYER_PREVIEW_LIBRARY = 'react'
         

# authorized exempt urls
ADDITIONAL_AUTH_EXEMPT_URLS = os.getenv(
    'ADDITIONAL_AUTH_EXEMPT_URLS',
    ()
)

if isinstance(ADDITIONAL_AUTH_EXEMPT_URLS, str):
    ADDITIONAL_AUTH_EXEMPT_URLS = tuple(map(str.strip, ADDITIONAL_AUTH_EXEMPT_URLS.split(',')))

AUTH_EXEMPT_URLS = ('/complete/*', '/login/*', '/api/o/*', '/api/roles', '/api/adminRole', '/api/users', '/o/token/*', '/o/authorize/*',) + ADDITIONAL_AUTH_EXEMPT_URLS

# geoserver settings
GEOSERVER_URL = os.getenv(
    'GEOSERVER_URL',
    'http://127.0.0.1:8080/geoserver/'
)
GEOSERVER_LOCAL_URL = os.getenv(
    'GEOSERVER_LOCAL_URL',
    GEOSERVER_URL
)
GEOSERVER_USER = os.getenv(
    'GEOSERVER_USER',
    'admin'
)
GEOSERVER_PASSWORD = os.getenv(
    'GEOSERVER_PASSWORD',
    'geoserver'
)
GEOSERVER_LOG = os.getenv(
    'GEOSERVER_LOG',
    '/opt/geonode/geoserver_data/logs/geoserver.log'
)
GEOSERVER_DATA_DIR = os.getenv(
    'GEOSERVER_DATA_DIR',
    '/opt/geonode/geoserver_data'
)
GEOGIG_DATASTORE_DIR = os.getenv(
    'GEOSERVER_DATA_DIR',
    '/opt/geonode/geoserver_data/geogig'
)
PG_DATASTORE = os.getenv('PG_DATASTORE', 'exchange_imports')
PG_GEOGIG = str2bool(os.getenv('PG_GEOGIG', 'True'))

OGC_SERVER = {
    'default': {
        'BACKEND': 'geonode.geoserver',
        'LOCATION': GEOSERVER_LOCAL_URL,
        'LOGIN_ENDPOINT': 'j_spring_oauth2_geonode_login',
        'LOGOUT_ENDPOINT': 'j_spring_oauth2_geonode_logout',
        'PUBLIC_LOCATION': GEOSERVER_URL,
        'USER': GEOSERVER_USER,
        'PASSWORD': GEOSERVER_PASSWORD,
        'MAPFISH_PRINT_ENABLED': True,
        'PRINT_NG_ENABLED': True,
        'GEONODE_SECURITY_ENABLED': True,
        'GEOGIG_ENABLED': True,
        'WMST_ENABLED': False,
        'BACKEND_WRITE_ENABLED': True,
        'WPS_ENABLED': True,
        'LOG_FILE': GEOSERVER_LOG,
        'GEOSERVER_DATA_DIR': GEOSERVER_DATA_DIR,
        'GEOGIG_DATASTORE_DIR': GEOGIG_DATASTORE_DIR,
        'DATASTORE': PG_DATASTORE,
        'PG_GEOGIG': PG_GEOGIG,
        'TIMEOUT': 10
    }
}

GEOSERVER_BASE_URL = OGC_SERVER['default']['PUBLIC_LOCATION'] + 'wms'
GEOGIG_DATASTORE_NAME = 'geogig-repo'

GEOFENCE = {
    'url': os.getenv('GEOFENCE_URL', "{}/geofence".format(GEOSERVER_LOCAL_URL.strip('/'))),
    'username': os.getenv('GEOFENCE_USERNAME', GEOSERVER_USER),
    'password':os.getenv('GEOFENCE_PASSWORD', GEOSERVER_PASSWORD)
}

MAP_BASELAYERS[0]['source']['url'] = (OGC_SERVER['default']
                                      ['PUBLIC_LOCATION'] + 'wms')

POSTGIS_URL = os.getenv(
    'POSTGIS_URL',
    'postgis://exchange:boundless@localhost:5432/exchange_data'
)
DATABASES['exchange_imports'] = dj_database_url.parse(
    POSTGIS_URL,
    conn_max_age=600
)
DATABASES['exchange_imports']['ENGINE'] = 'django.contrib.gis.db.backends.postgis'

WGS84_MAP_CRS = str2bool(os.getenv('WGS84_MAP_CRS', 'False'))
if WGS84_MAP_CRS:
    DEFAULT_MAP_CRS = "EPSG:4326"

# local pycsw
CATALOGUE['default']['URL'] = '%s/catalogue/csw' % SITEURL.rstrip('/')

'''
unified search settings
ES_UNIFIED_SEARCH must be set to True
Elastic Search for both Registry and GeoNode must running
on same elasticsearch instance at ES_URL
REGISTRY_URL must be set in order to provide links to Registry
'''
ES_UNIFIED_SEARCH = str2bool(os.getenv('ES_UNIFIED_SEARCH', 'False'))

# haystack settings
ES_URL = os.getenv('ES_URL', 'http://127.0.0.1:9200/')
ES_ENGINE = os.getenv(
    'ES_ENGINE',
    'haystack.backends.elasticsearch_backend.ElasticsearchSearchEngine'
)
HAYSTACK_SEARCH = str2bool(os.getenv('HAYSTACK_SEARCH', 'False'))
if ES_UNIFIED_SEARCH:
    HAYSTACK_SEARCH = True
    HAYSTACK_FACET_COUNTS = True
if HAYSTACK_SEARCH:
    HAYSTACK_SIGNAL_PROCESSOR = 'haystack.signals.RealtimeSignalProcessor'
    HAYSTACK_CONNECTIONS = {
        'default': {
            'ENGINE': ES_ENGINE,
            'URL': ES_URL,
            'INDEX_NAME': 'exchange',
        },
    }
    INSTALLED_APPS = (
        'haystack',
    ) + INSTALLED_APPS


# amqp settings
BROKER_URL = os.getenv('BROKER_URL', 'amqp://guest:guest@localhost:5672/')
CELERY_ALWAYS_EAGER = False
NOTIFICATION_QUEUE_ALL = not CELERY_ALWAYS_EAGER
NOTIFICATION_LOCK_LOCATION = LOCAL_ROOT
SKIP_CELERY_TASK = False
CELERY_DEFAULT_EXCHANGE = 'exchange'
CELERYBEAT_SCHEDULER = 'djcelery.schedulers.DatabaseScheduler'
CELERY_RESULT_BACKEND = 'rpc' + BROKER_URL[4:]
CELERYD_PREFETCH_MULTIPLIER = 25
CELERY_TASK_RESULT_EXPIRES = 18000  # 5 hours.
CELERY_ENABLE_UTC = False
CELERY_TIMEZONE = TIME_ZONE
CELERY_IMPORTS += ('exchange.tasks',)

# audit settings
AUDIT_ENABLED = str2bool(os.getenv('AUDIT_ENABLED', 'True'))
if AUDIT_ENABLED:
    INSTALLED_APPS = INSTALLED_APPS + (
        'exchange.audit',
    )

    AUDIT_TO_FILE = str2bool(os.getenv('AUDIT_TO_FILE', 'False'))
    AUDIT_LOGFILE_LOCATION = os.getenv(
        'AUDIT_LOGFILE_LOCATION',
        os.path.join(LOCAL_ROOT, 'exchange_audit_log.json')
    )

# Logging settings
# 'DEBUG', 'INFO', 'WARNING', 'ERROR', or 'CRITICAL'
DJANGO_LOG_LEVEL = os.getenv('DJANGO_LOG_LEVEL', 'ERROR')
# Commenting out logging until it can be modified to log errors correctly
'''
installed_apps_conf = {
    'handlers': ['console'],
    'level': DJANGO_LOG_LEVEL,
}

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format':
                ('%(levelname)s %(asctime)s %(module)s %(process)d %(thread)d'
                 ' %(message)s'),
        },
    },
    'handlers': {
        'console': {
            'level': DJANGO_LOG_LEVEL,
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        }
    },
    'loggers': {
        app: copy.deepcopy(installed_apps_conf) for app in INSTALLED_APPS
    },
    'root': {
        'handlers': ['console'],
        'level': DJANGO_LOG_LEVEL
    },
}

LOGGING['loggers']['django.db.backends'] = {
    'handlers': ['console'],
    'propagate': False,
    'level': 'WARNING',  # Django SQL logging is too noisy at DEBUG
}
'''
# Authentication Settings

# ldap
AUTH_LDAP_SERVER_URI = os.getenv('AUTH_LDAP_SERVER_URI', None)
LDAP_SEARCH_DN = os.getenv('LDAP_SEARCH_DN', None)
if all([AUTH_LDAP_SERVER_URI, LDAP_SEARCH_DN]):
    from ._ldap import *   # noqa

# geoaxis
GEOAXIS_ENABLED = str2bool(os.getenv('GEOAXIS_ENABLED', 'False'))
if GEOAXIS_ENABLED:
    GEOAXIS_HEADER = os.getenv('GEOAXIS_HEADER', None)
    AUTHENTICATION_BACKENDS = (
        'django.contrib.auth.backends.RemoteUserBackend',
    ) + AUTHENTICATION_BACKENDS
    for i, middleware in enumerate(MIDDLEWARE_CLASSES):
        # Put custom middleware class after AuthenticationMiddleware
        if middleware == 'django.contrib.auth.middleware.AuthenticationMiddleware':
            MIDDLEWARE_CLASSES = list(MIDDLEWARE_CLASSES)
            MIDDLEWARE_CLASSES.insert(i+1, 'exchange.auth.middleware.GeoAxisMiddleware')


# NEED TO UPDATE DJANGO_MAPLOOM FOR ONLY THIS ONE VALUE
REGISTRY = str2bool(os.getenv('ENABLE_REGISTRY', 'False'))
REGISTRYURL = os.getenv('REGISTRYURL', None)
REGISTRY_CAT = os.getenv('REGISTRY_CAT', 'registry')
REGISTRY_LOCAL_URL = os.getenv('REGISTRY_LOCAL_URL', 'http://localhost:8001')

# NearSight Options, adding NEARSIGHT_ENABLED to env will enable nearsight.
NEARSIGHT_ENABLED = str2bool(os.getenv('NEARSIGHT_ENABLED', 'False'))
if NEARSIGHT_ENABLED:
    NEARSIGHT_UPLOAD_PATH = os.getenv('NEARSIGHT_UPLOAD_PATH', '/opt/nearsight/store')
    NEARSIGHT_LAYER_PREFIX = os.getenv('NEARSIGHT_LAYER_PREFIX', 'nearsight')
    NEARSIGHT_CATEGORY_NAME = os.getenv('NEARSIGHT_CATEGORY_NAME', 'NearSight')
    NEARSIGHT_GEONODE_RESTRICTIONS = os.getenv('NEARSIGHT_GEONODE_RESTRICTIONS', 'NearSight Data')
    DATABASES['nearsight'] = DATABASES['exchange_imports']
    CACHES = locals().get('CACHES', {})
    CACHES['nearsight'] = CACHES.get('nearsight', {
        'BACKEND': 'django.core.cache.backends.filebased.FileBasedCache',
        'LOCATION': NEARSIGHT_UPLOAD_PATH,
    })
    CACHES['default'] = CACHES.get('default', CACHES.get('nearsight'))
    NEARSIGHT_SERVICE_UPDATE_INTERVAL = le(os.getenv('NEARSIGHT_SERVICE_UPDATE_INTERVAL', '5'))
    SSL_VERIFY = str2bool(os.getenv('SSL_VERIFY', 'False'))
    INSTALLED_APPS += ('nearsight',)

# If django-osgeo-importer is enabled, give it the settings it needs...
if 'osgeo_importer' in INSTALLED_APPS:
    import pyproj
    # Point django-osgeo-importer, if enabled, to the Exchange database
    OSGEO_DATASTORE = 'exchange_imports'
    # Tell it to use the GeoNode compatible mode
    OSGEO_IMPORTER_GEONODE_ENABLED = True
    # Tell celery to load its tasks
    CELERY_IMPORTS += ('osgeo_importer.tasks',)
    # override GeoNode setting so importer UI can see when tasks finish
    CELERY_IGNORE_RESULT = False
    IMPORT_HANDLERS = [
        # If GeoServer handlers are enabled, you must have an instance of
        # geoserver running.
        # Warning: the order of the handlers here matters.
        'osgeo_importer.handlers.FieldConverterHandler',
        'osgeo_importer.handlers.geoserver.GeoserverPublishHandler',
        'osgeo_importer.handlers.geoserver.GeoserverPublishCoverageHandler',
        'osgeo_importer.handlers.geoserver.GeoServerTimeHandler',
        'osgeo_importer.handlers.geoserver.GeoWebCacheHandler',
        'osgeo_importer.handlers.geoserver.GeoServerBoundsHandler',
        'osgeo_importer.handlers.geoserver.GenericSLDHandler',
        'osgeo_importer.handlers.geonode.GeoNodePublishHandler',
        'osgeo_importer.handlers.geoserver.GeoServerStyleHandler',
        'osgeo_importer.handlers.geonode.GeoNodeMetadataHandler',
        'exchange.importer.geonode_timeextent_handler.GeoNodeTimeExtentHandler',
    ]
    PROJECTION_DIRECTORY = os.path.join(
        os.path.dirname(pyproj.__file__),
        'data/'
    )

FILESERVICE_CONFIG = {
    'store_dir': os.getenv('FILESERVICE_MEDIA_ROOT', os.path.join(MEDIA_ROOT, 'fileservice')),
    'types_allowed': ['.jpg', '.jpeg', '.png'],
    'streaming_supported': False
}

try:
    from local_settings import *  # noqa
except ImportError:
    pass

# Use https:// scheme in Gravatar URLs
AVATAR_GRAVATAR_SSL = True

# TODO: disable pickle serialization when we can ensure JSON works everywhere
# CELERY_ACCEPT_CONTENT = ['json']
# CELERY_TASK_SERIALIZER = 'json'
# CELERY_RESULT_SERIALIZER = 'json'
SESSION_COOKIE_AGE = 60 * 60 * 24

# Set default access to layers to all, user will need to deselect the checkbox
# manually
DEFAULT_ANONYMOUS_VIEW_PERMISSION = str2bool(os.getenv('DEFAULT_ANONYMOUS_VIEW_PERMISSION', 'True'))
DEFAULT_ANONYMOUS_DOWNLOAD_PERMISSION = str2bool(os.getenv('DEFAULT_ANONYMOUS_DOWNLOAD_PERMISSION', 'True'))

ENABLE_SOCIAL_LOGIN = str2bool(os.getenv('ENABLE_SOCIAL_LOGIN', 'False'))

# Should always be set to true if we're behind a proxy
USE_X_FORWARDED_HOST = True
if SITEURL.startswith('https'):
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

ACCOUNT_EMAIL_UNIQUE = str2bool(os.getenv('ACCOUNT_EMAIL_UNIQUE', 'True'))

if ENABLE_SOCIAL_LOGIN:
    SOCIAL_AUTH_NEW_USER_REDIRECT_URL = '/'

    AUTHENTICATION_BACKENDS += (
        'social_core.backends.google.GoogleOpenId',
        'social_core.backends.google.GoogleOAuth2',
        'social_core.backends.facebook.FacebookOAuth2',
        'exchange.auth.backends.auth0.AuthZeroOAuth2',
    )

    DEFAULT_AUTH_PIPELINE = (
        'social_core.pipeline.social_auth.social_details',
        'social_core.pipeline.social_auth.social_uid',
        'social_core.pipeline.social_auth.auth_allowed',
        'social_core.pipeline.social_auth.social_user',
        'social_core.pipeline.user.get_username',
        'social_core.pipeline.mail.mail_validation',
        'social_core.pipeline.social_auth.associate_by_email',
        'social_core.pipeline.user.create_user',
        'social_core.pipeline.social_auth.associate_user',
        'social_core.pipeline.social_auth.load_extra_data',
        'social_core.pipeline.user.user_details'
    )

    SOCIAL_AUTH_AUTH0_KEY = os.getenv('OAUTH_AUTH0_KEY', None)
    SOCIAL_AUTH_AUTH0_SECRET = os.getenv('OAUTH_AUTH0_SECRET', None)
    SOCIAL_AUTH_AUTH0_HOST = os.getenv('OAUTH_AUTH0_HOST', None)
    ENABLE_AUTH0_LOGIN = isValid(SOCIAL_AUTH_AUTH0_KEY)
    AUTH0_APP_NAME = os.getenv('AUTH0_APP_NAME', 'Connect')
    OAUTH_AUTH0_ADMIN_ROLES = os.getenv(
        'OAUTH_AUTH0_ADMIN_ROLES', 
        ""
    )
    OAUTH_AUTH0_ALLOWED_ROLES = os.getenv(
        'OAUTH_AUTH0_ALLOWED_ROLES', 
        ""
    )

    if OAUTH_AUTH0_ADMIN_ROLES.strip():
        AUTH0_ADMIN_ROLES = map(str.strip, OAUTH_AUTH0_ADMIN_ROLES.split(','))
    if OAUTH_AUTH0_ALLOWED_ROLES.strip():
        AUTH0_ALLOWED_ROLES = map(str.strip, OAUTH_AUTH0_ALLOWED_ROLES.split(','))

    SOCIAL_AUTH_FACEBOOK_KEY = os.getenv('OAUTH_FACEBOOK_KEY', None)
    SOCIAL_AUTH_FACEBOOK_SECRET = os.getenv('OAUTH_FACEBOOK_SECRET', None)
    OAUTH_FACEBOOK_SCOPES = os.getenv('OAUTH_FACEBOOK_SCOPES', 'email')
    SOCIAL_AUTH_FACEBOOK_SCOPE = map(str.strip, OAUTH_FACEBOOK_SCOPES.split(','))
    SOCIAL_AUTH_FACEBOOK_PROFILE_EXTRA_PARAMS = {
        'fields': os.getenv('OAUTH_FACEBOOK_PROFILE_EXTRA_PARAMS', 'id,name,email'),
    }
    ENABLE_FACEBOOK_LOGIN = isValid(SOCIAL_AUTH_FACEBOOK_KEY)

    SOCIAL_AUTH_GOOGLE_OAUTH2_KEY = os.getenv('OAUTH_GOOGLE_KEY', None)
    SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET = os.getenv('OAUTH_GOOGLE_SECRET', None)
    ENABLE_GOOGLE_LOGIN = isValid(SOCIAL_AUTH_GOOGLE_OAUTH2_KEY)

    SOCIAL_AUTH_GEOAXIS_KEY = os.getenv('OAUTH_GEOAXIS_KEY', None)
    SOCIAL_AUTH_GEOAXIS_SECRET = os.getenv('OAUTH_GEOAXIS_SECRET', None)
    SOCIAL_AUTH_GEOAXIS_HOST = os.getenv('OAUTH_GEOAXIS_HOST', None)
    OAUTH_GEOAXIS_USER_FIELDS = os.getenv('OAUTH_GEOAXIS_USER_FIELDS', 'username, email, last_name, first_name')
    SOCIAL_AUTH_GEOAXIS_USER_FIELDS = map(str.strip, OAUTH_GEOAXIS_USER_FIELDS.split(','))
    OAUTH_GEOAXIS_SCOPES = os.getenv('OAUTH_GEOAXIS_SCOPES', 'UserProfile.me')
    SOCIAL_AUTH_GEOAXIS_SCOPE = map(str.strip, OAUTH_GEOAXIS_SCOPES.split(','))
    ENABLE_GEOAXIS_LOGIN = isValid(SOCIAL_AUTH_GEOAXIS_KEY)
    if SITEURL.startswith('https'):
        SOCIAL_AUTH_REDIRECT_IS_HTTPS = True
    # GeoAxisOAuth2 will cause all login attempt to fail if SOCIAL_AUTH_GEOAXIS_HOST is None
    if ENABLE_GEOAXIS_LOGIN:
        AUTHENTICATION_BACKENDS += (
            'exchange.auth.backends.geoaxis.GeoAxisOAuth2',
        )

# MapLoom search options
NOMINATIM_URL = os.getenv('NOMINATIM_URL', '//nominatim.openstreetmap.org')
GEOQUERY_ENABLED = str2bool(os.getenv('GEOQUERY_ENABLED', 'False'))
GEOQUERY_URL = os.getenv('GEOQUERY_URL', None)
if GEOQUERY_ENABLED:
    NOMINATIM_ENABLED = False
else:
    NOMINATIM_ENABLED = True

SEARCH_FILTERS['HOST_ENABLED'] = True
MAP_CLIENT_USE_CROSS_ORIGIN_CREDENTIALS = str2bool(os.getenv(
    'MAP_CLIENT_USE_CROSS_ORIGIN_CREDENTIALS',
    'False'
))
