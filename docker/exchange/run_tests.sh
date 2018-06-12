#!/bin/bash

set -e

pushd /code
pip install pytest-cov
export DJANGO_SETTINGS_MODULE='exchange.settings'
export PYTEST=1
py.test --junitxml=/code/docker/data/pytest-results.xml \
        --cov-report term \
        --cov=exchange exchange/tests/views_test.py \
        --disable-pytest-warnings
popd
