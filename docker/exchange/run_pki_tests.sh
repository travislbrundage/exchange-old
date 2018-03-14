#!/bin/bash

set -e

pip show pytest > /dev/null || pip install pytest

pushd /code > /dev/null
  # override some settings in Exchange, like default DEBUG logging
  export DJANGO_SETTINGS_MODULE='exchange.pki.tests.docker_test_settings'
  pytest --disable-warnings \
    --color=auto \
    --exitfirst \
    --showlocals \
    --full-trace \
    -k test \
    exchange/tests/pki_test.py
#  python manage.py test exchange.tests.pki_test -v 3 --failfast
popd > /dev/null
