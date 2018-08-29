#!/bin/bash

set -e


pip show pip 2>&1 | grep -q 'should consider upgrading' \
  && pip install --upgrade pip || true

pip show pytest > /dev/null || pip install pytest

pushd /code > /dev/null
  # For overriding some settings in Exchange, like default DEBUG logging
  export DJANGO_SETTINGS_MODULE='exchange.settings'
  pytest --disable-warnings \
    --color=auto \
    --exitfirst \
    --showlocals \
    -k test \
    exchange/tests/pki_test.py
#  python manage.py test exchange.tests.pki_test -v 3 --failfast
popd > /dev/null
