import os
import sys

sys.path.insert(
    0,
    os.path.dirname(
        os.path.dirname(
            os.path.dirname(
                os.path.realpath(__file__))))
)

TESTDIR = os.path.dirname(os.path.realpath(__file__))

SECRET_KEY = 'fake-key'

INSTALLED_APPS = [
    "pki",
    "pki.tests",
]

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(TESTDIR, 'development.db'),
        'TEST': {
            'NAME': os.path.join(TESTDIR, 'development.db'),
        }
    }
}
