#!/bin/bash

set -e

# trying to keep the images lean
apt-get update -y
apt-get install -y gcc

pushd /code
pip install pytest-cov
export DJANGO_SETTINGS_MODULE='exchange.settings'
export PYTEST=1
py.test --junitxml=/code/docker/data/pytest-results.xml \
        --cov-report term \
        --cov=exchange exchange/tests/ \
        --disable-pytest-warnings
popd
