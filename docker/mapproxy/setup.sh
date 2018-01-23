#!/usr/bin/env bash

apt-get -y update
# apt-get -y upgrade

### base
#DEBIAN_FRONTEND=noninteractive apt-get install -y \
#  supervisor (use pip)


### nginx
DEBIAN_FRONTEND=noninteractive apt-get install -y \
  ca-certificates \
  openssl \
  curl \
  nginx-light


### mapproxy
# Culled from work by Tim Sutton<tim@kartoza.com>
# See: https://github.com/kartoza/docker-mapproxy

DEBIAN_FRONTEND=noninteractive apt-get install -y \
  python-imaging \
  python-yaml \
  libproj-dev \
  libgeos-dev \
  python-lxml \
  libgdal-dev \
  build-essential \
  python-dev \
  libjpeg-dev \
  zlib1g-dev \
  libfreetype6-dev \
  python-virtualenv

pip2 install \
  supervisor \
  supervisor-stdout \
  Shapely \
  Pillow \
  MapProxy \
  uwsgi

### cleanup
apt-get -q clean
apt-get -q purge
rm -rf /var/lib/apt/lists/*
