#!/bin/bash

set -e

pushd /code
pip install pytest-cov
export DJANGO_SETTINGS_MODULE='exchange.settings'
export PYTEST=1
py.test --cov-report term \
        --cov=exchange exchange/tests/ \
        --disable-pytest-warnings
popd
