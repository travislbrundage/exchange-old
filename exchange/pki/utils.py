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
    return '{0}{1}'.format(parts.hostname,
                           ":{0}".format(port) if port else '')


def requests_base_url(url):
    parts = urlparse(url)
    return '{0}://{1}'.format(parts.scheme, hostname_port(url))


def file_readable(a_file):
    return all([
        os.path.exists(a_file),
        os.path.isfile(a_file),
        os.access(a_file, os.R_OK)
    ])


def pki_file(a_file):
    return os.path.join(get_pki_dir(), a_file)
