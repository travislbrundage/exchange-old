# -*- coding: utf-8 -*-
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
import re
import logging

# noinspection PyCompatibility
from urlparse import urlparse
from urllib import quote, unquote

from django.conf import settings

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
    return u"{0}{1}".format(parts.hostname,
                            u":{0}".format(port) if port else '')


def requests_base_url(url):
    parts = urlparse(url)
    return u"{0}://{1}".format(parts.scheme, hostname_port(url))


def pki_prefix():
    exchange_local = settings.EXCHANGE_LOCAL_URL.rstrip('/')
    return "{0}/pki/".format(exchange_local)


def pki_route(url):
    """
    Reroutes a service url through the 'pki' internal proxy
    :param url: Original service url
    :return: Modified url prepended with internal proxy route
    Ex: url = https://myserver.com:port/geoserver/wms
    return <site:scheme>://<site>/pki/myserver.com%3Aport/geoserver/wms
    """
    url = normalize_hostname(url)
    parts = urlparse(url)
    # TODO: Consider leaving scheme; otherwise, https is assumed later
    url = re.sub(parts.scheme, '', url, count=1, flags=re.I)
    url = url.replace('://', '', 1)

    return "{0}{1}".format(pki_prefix(), quote(url))


def pki_route_reverse(url):
    """
    Revert possibly rewritten /pki-proxied URL back to original value

    NOTE: Since no origin scheme is recorded (could be, in rewritten pki
    proxy path), https is assumed.

    :param url: A possibly rewritten /pki-proxied URL
    :type url: str | unicode
    :return: URL reverted back to value prior to rewriting
    """
    if url.startswith(pki_prefix()):
        url = "https://{0}".format(
            unquote(url.replace(pki_prefix(), '')))
    return url


def file_readable(a_file):
    return all([
        os.path.exists(a_file),
        os.path.isfile(a_file),
        os.access(a_file, os.R_OK)
    ])


def pki_file(a_file):
    return os.path.join(get_pki_dir(), a_file)
