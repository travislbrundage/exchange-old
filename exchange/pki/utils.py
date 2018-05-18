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
from urlparse import urlparse, urlsplit, urljoin
from urllib import quote, unquote, quote_plus, unquote_plus

from django.conf import settings

from .settings import get_pki_dir


logger = logging.getLogger(__name__)


def protocol_relative_url(url):
    return url.startswith('//') or url.startswith(u'//')


def protocol_relative_to_scheme(url, scheme='https'):
    """
    Convert a protocol relative (starts with //) URL to one with a scheme
    :param url: Protocol relative (or not) URL
    :param scheme: Pass in request.scheme if available, otherwise https is
    assumed, even if it might be unavailable at the endpoint, because there is
    no way of knowing at this point.
    :rtype: basestring
    """
    if protocol_relative_url(url):
        if isinstance(url, unicode):  # noqa
            return u'{0}:{1}'.format(scheme, url)
        else:
            return '{0}:{1}'.format(scheme, url)
    return url


def relative_to_absolute_url(url, scheme='https'):
    parts = urlsplit(url)
    if protocol_relative_url(url) or not parts.scheme:
        if parts.netloc:
            return protocol_relative_to_scheme(url, scheme=scheme)
        else:
            site_parts = urlsplit(settings.SITEURL.rstrip('/'))
            current_uri = '{scheme}://{host}{path}'.format(
                scheme=site_parts.scheme,
                host=site_parts.netloc,
                path=parts.path)
            return urljoin(current_uri, url)  # rejoin any query/fragment
    return url


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


def pki_site_prefix():
    exchange_site = settings.SITEURL.rstrip('/')
    return "{0}/pki/".format(exchange_site)


def _pki_prefixes():
    return [pki_prefix(), pki_site_prefix()]


def has_pki_prefix(url):
    for prefix in _pki_prefixes():
        if url.startswith(prefix):
            return True
    return False


def pki_route(url, site=False):
    """
    Reroutes a service url through the 'pki' internal proxy
    :param url: Original service url
    :param site: Whether to build with pki_site_prefix instead
    :return: Modified url prepended with internal proxy route
    Ex: url = https://myserver.com:port/geoserver/wms
    return <site:scheme>://<site>/pki/myserver.com%3Aport/geoserver/wms
    """
    url = normalize_hostname(url)
    parts = urlparse(url)
    # TODO: Consider leaving scheme; otherwise, https is assumed later
    url = re.sub(parts.scheme, '', url, count=1, flags=re.I)
    url = url.replace('://', '', 1)

    return "{0}{1}".format(
        pki_site_prefix() if site else pki_prefix(), quote(url))


def pki_route_reverse(url):
    """
    Revert possibly rewritten /pki-proxied URL back to original value.

    NOTE: Since no origin scheme is recorded (could be, in rewritten pki
    proxy path), https is assumed.

    :param url: A possibly rewritten /pki-proxied URL
    :type url: str | unicode
    :return: URL reverted back to value prior to rewriting
    """
    for prefix in _pki_prefixes():
        if url.startswith(prefix):
            return "https://{0}".format(unquote(url.replace(prefix, '', 1)))
    return url


def proxy_prefix():
    return "{0}{1}".format(settings.SITEURL.rstrip('/'), settings.PROXY_URL)


def has_proxy_prefix(url):
    return True if url.startswith(proxy_prefix()) else False


def proxy_route(url):
    return "{0}{1}".format(proxy_prefix(), quote_plus(url))


def proxy_route_reverse(url):
    if url.startswith(proxy_prefix()):
        return unquote_plus(url.replace(proxy_prefix(), '', 1))
    return url


def pki_to_proxy_route(url):
    """Converts a URL with a pki_route prefix to a settings.PROXY_URL one"""
    if has_pki_prefix(url):
        return proxy_route(pki_route_reverse(url))
    return url


def file_readable(a_file):
    return all([
        os.path.exists(a_file),
        os.path.isfile(a_file),
        os.access(a_file, os.R_OK)
    ])


def pki_file(a_file):
    return os.path.join(get_pki_dir(), a_file)
