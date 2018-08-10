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

import logging

from requests import Session
from requests.adapters import HTTPAdapter
from requests.exceptions import InvalidSchema

try:
    # Nix automatic support for pyOpenSSL in urllib3, as it will fail with:
    #  PyOpenSSLContext object has no attribute 'load_default_certs'
    #  (which we need for PKI functionality)
    # Also, any Python > 2.7.9 will do for SSL/SNI support (for now):
    # http://urllib3.readthedocs.io/en/latest/advanced-usage.html#ssl-warnings
    from urllib3.contrib import pyopenssl
    from urllib3.util import IS_PYOPENSSL
    if IS_PYOPENSSL:
        pyopenssl.extract_from_urllib3()
except ImportError:
    pyopenssl = None
    IS_PYOPENSSL = None

from .models import has_ssl_config
from .utils import requests_base_url, normalize_hostname
from .ssl_adapter import SslContextAdapter


logger = logging.getLogger(__name__)


class SslContextSession(Session):
    """
    A requests Session that enables manipulation of SSL adapter context.

    Custom SslContextAdapters are applied individually, relative to destination
    URL's hostname:port.
    """

    # noinspection PyUnusedLocal
    def __init__(self, *args, **kwargs):

        super(SslContextSession, self).__init__()

        # Clear default, fallback 'https://' adapter;
        # all https adapters in our session MUST be unique to a fqdn[:port]
        # It's up to admin what (if any) adapter gets mapped to all https
        # connections, e.g. '*.*' wildcard mapping --> default SslConfig
        # NOTE: such a wildcard mapping WON'T create an 'https://' adapter
        self.clear_https_adapters()

    def clear_https_adapters(self):
        """Clears just the https:// prefixed cached adapters"""
        for adptr in self.adapters:
            if adptr.startswith('https://'):
                self.adapters[adptr].close()
                del self.adapters[adptr]

    def mount_sslcontext_adapter(self, url):
        # IMPORTANT: base_url is (scheme://hostname:port), not full url.
        # Note: urllib3 (as of 1.22) seems to care about case when matching
        # the hostname to the peer server's SSL cert, in contrast to spec,
        # which says matches should be case-insensitive (this is a bug):
        #   https://tools.ietf.org/html/rfc5280#section-4.2.1.6
        #   https://tools.ietf.org/html/rfc6125 <-- best practices
        # normalize_hostname() handles this bug
        base_url = requests_base_url(normalize_hostname(url))

        try:
            self.get_adapter(base_url)
            # This debug text will flood log; enable temporarily during dev
            # logger.debug(u'Using session SslContextAdapter for {0}'
            #              .format(base_url))
        except InvalidSchema:
            # TODO: via_query=True here *may* cause excessive db calls; if so,
            #       it can be False, but then returned value is dependent upon
            #       whether pattern cache has been recently updated on host.
            if has_ssl_config(base_url, via_query=True):
                self.mount(base_url, SslContextAdapter(base_url))
                logger.info(u'SslContext Session adapter added for {0}'
                            .format(base_url))
            else:
                self.mount(base_url, HTTPAdapter())
                logger.debug(u'Base HTTP session adapter add {0}'
                             .format(base_url))

    def send(self, request, **kwargs):
        # Setting up the adapter just before sending allows adapters to be
        # added during yielded redirects in Session.resolve_redirects(...)
        # This is critical for redirects also requiring SslConfigs, e.g. PKI
        if request.url.lower().startswith('https'):
            self.mount_sslcontext_adapter(request.url)

        return super(SslContextSession, self).send(request, **kwargs)


# global, so base_url -> adapter registrations are cached across calls
https_client = SslContextSession()
