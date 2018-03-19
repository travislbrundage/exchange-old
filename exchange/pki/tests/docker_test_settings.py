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

from exchange.settings.default import *  # noqa

# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.sqlite3',
#         'NAME': dj_database_url.parse(DATABASE_URL, conn_max_age=600),
#         'TEST': {
#             'NAME': dj_database_url.parse(DATABASE_URL, conn_max_age=600),
#         }
#     }
# }

DJANGO_IGNORED_WARNINGS = {
    'RemovedInDjango18Warning',
    'RemovedInDjango19Warning',
    'RuntimeWarning: DateTimeField',
}


# See: https://stackoverflow.com/a/30716923
def filter_django_warnings(record):
    for ignored in DJANGO_IGNORED_WARNINGS:
        if ignored in record.args[0]:
            return False
    return True


# Logging settings
# 'DEBUG', 'INFO', 'WARNING', 'ERROR', or 'CRITICAL'
DJANGO_LOG_LEVEL = os.getenv('DJANGO_LOG_LEVEL', 'DEBUG')
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format':
                ('%(levelname)s %(asctime)s %(pathname)s %(process)d '
                 '%(thread)d %(message)s'),
        },
    },
    'handlers': {
        'console': {
            'level': DJANGO_LOG_LEVEL,
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        }
    },
    'filters': {
        'ignore_django_warnings': {
            '()': 'django.utils.log.CallbackFilter',
            'callback': filter_django_warnings,
        },
    },
    'loggers': {
        'py.warnings': {
            'handlers': ['console', ],
            'filters': ['ignore_django_warnings', ],
        },
        # 'pki': {
        #     'handlers': ['console'],
        #     'level': DJANGO_LOG_LEVEL,
        # },
        # 'urllib3': {
        #     'handlers': ['console'],
        #     'level': DJANGO_LOG_LEVEL,
        # },
        # 'requests': {
        #     'handlers': ['console'],
        #     'level': DJANGO_LOG_LEVEL,
        # },
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
