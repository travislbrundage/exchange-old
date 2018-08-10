#########################################################################
#
# Copyright (C) 2018 Boundless Spatial
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


def str2bool(v):
    if v and len(v) > 0:
        return v.lower() in ("yes", "true", "t", "1")
    else:
        return False


TESTDIR = os.path.dirname(os.path.realpath(__file__))

SECRET_KEY = 'fake-key'

ROOT_URLCONF = 'pki.urls'
EXTRA_LANG_INFO = {}

INSTALLED_APPS = [
    'pki.apps.PkiTestAppConfig',
    'pki.tests',
]

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
)

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(TESTDIR, 'development.db'),
        'TEST': {
            'NAME': os.path.join(TESTDIR, 'development.db'),
        }
    }
}

SITEURL = os.getenv('SITEURL', "http://nginx.boundless.test/")
EXCHANGE_LOCAL_URL = os.getenv('EXCHANGE_LOCAL_URL',
                               'http://exchange.boundless.test:8000')
PROXY_URL = '/proxy/?url='

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

# Force max length validation on encrypted password fields
ENFORCE_MAX_LENGTH = 1

# Logging settings
# 'DEBUG', 'INFO', 'WARNING', 'ERROR', or 'CRITICAL'
DJANGO_LOG_LEVEL = os.getenv('DJANGO_LOG_LEVEL', 'DEBUG')
LOGGING = {
    'version': 1,
    'disable_existing_loggers': True,
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
    'loggers': {},
    # 'loggers': {
    #     'pki': {
    #         'handlers': ['console'],
    #         'level': DJANGO_LOG_LEVEL,
    #     },
    #     'urllib3': {
    #         'handlers': ['console'],
    #         'level': DJANGO_LOG_LEVEL,
    #     },
    #     'requests': {
    #         'handlers': ['console'],
    #         'level': DJANGO_LOG_LEVEL,
    #     },
    # },
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
