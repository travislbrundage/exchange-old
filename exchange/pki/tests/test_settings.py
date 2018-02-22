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

TESTDIR = os.path.dirname(os.path.realpath(__file__))

SECRET_KEY = 'fake-key'

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
