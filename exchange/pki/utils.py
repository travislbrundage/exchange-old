# -*- coding: utf-8 -*-
#########################################################################
#
# Copyright (C) 2017 Boundless Spatial
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
import re
import logging

# noinspection PyCompatibility
from urlparse import urlparse
from urllib import quote

from .settings import get_pki_dir


logger = logging.getLogger(__name__)


def normalize_hostname(url):
    """
    Replace url with same URL, but with lowercased hostname
    :param url: A URL
    :rtype: basestring
    """
    parts = urlparse(url)
    return re.sub(parts.hostname, parts.hostname, url, count=1, flags=re.I)


def hostname_port(url):
    parts = urlparse(url)
    port = parts.port
    return parts.hostname + ":{0}".format(port) if port else ''


def requests_base_url(url):
    parts = urlparse(url)
    return '{0}://{1}'.format(parts.scheme, hostname_port(url))


def pki_route(request, url):
    """
    Reroutes a service url through our internal proxy
    :param request: Request object from Django
    :type request: django.http.HttpRequest
    :param url: Original service url
    :return: Modified url via internal proxy
    Ex: url = https://myserver.com:port/geoserver/wms
    return <site:scheme>://<site>/pki/myserver.com%3Aport/geoserver/wms
    """
    url = normalize_hostname(url)
    parts = urlparse(url)
    url = re.sub(parts.scheme, '', url, count=1, flags=re.I)
    url = url.replace('://', '', 1)

    # Determine local host and port that project is running on.
    # Live host differs from SITEURL, which can differ from request.get_host().
    # Under docker-compose setups, SITEURL is localhost, which may be the Web
    # entrypoint on the same host or a reverse proxy sitting in front of it;
    # while request.get_host() may be like SITEURL, plus may be a domain alias.
    live_host = os.getenv('DJANGO_LIVE_TEST_SERVER_ADDRESS', None)
    server_host = request.META.get('SITEURL', None)
    server_port = request.META.get('SERVER_PORT', None)
    server_scheme = None
    if server_host:
        s_parts = urlparse(server_host)
        if s_parts.hostname:
            s_port = s_parts.port or server_port
            server_host = '{0}{1}'.format(
                s_parts.hostname, (':{0}'.format(s_port) if s_port else ''))
            server_scheme = s_parts.scheme
        else:
            server_host = None
    # request.get_host() is fallback, but not good if reverse proxy exists
    host = live_host or server_host or request.get_host()

    return '{0}://{1}/pki/{2}'.format(
        (server_scheme or request.scheme), host, quote(url))


def file_readable(a_file):
    return all([
        os.path.exists(a_file),
        os.path.isfile(a_file),
        os.access(a_file, os.R_OK)
    ])


def pki_file(a_file):
    return os.path.join(get_pki_dir(), a_file)
