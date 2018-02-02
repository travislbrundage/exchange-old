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

import re
import logging

# noinspection PyCompatibility
from urlparse import urlparse
from django.contrib.sites.models import Site
from urllib import quote


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


def pki_route(url):
    '''
    Reroutes a service url through our internal proxy
    :param url: Original service url
    :return: Modified url via internal proxy
    Ex: url = https://myserver.com:port/geoserver/wms
    return https://<site>/pki/myserver.com%3Aport/geoserver/wms
    '''
    site_url = Site.objects.get_current().domain
    pki_url = 'https://' + site_url + '/pki' + quote(url).lower()
    return pki_url
