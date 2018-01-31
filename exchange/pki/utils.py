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
# We need import ssl to fail if it can't be imported.
# urllib3.create_urllib3_context() will create a context without support for
# PKI private key password otherwise.
import ssl

from ssl import Purpose, SSLError
from requests.adapters import HTTPAdapter
# noinspection PyPackageRequirements
from urllib3.util.ssl_ import (create_urllib3_context,
                               resolve_ssl_version,
                               resolve_cert_reqs)
# noinspection PyPackageRequirements
from urllib3.util.retry import Retry
# noinspection PyCompatibility
from urlparse import urlparse

from .settings import SSL_DEFAULT_CONFIG, SSL_CONFIGS, SSL_CONFIG_MAP


class SslContextAdapter(HTTPAdapter):
    """
    A requests TransportAdapter that enables manipulation of its SSL context.

    For some defaults, see `import ssl; dir(ssl)` for what your Python's ssl
    module supports via the dynamically loaded symbols from OpenSSL.

    :param context_create_options: ssl.context creation options, accepts any:
        (defaults shown are supplied by urllib3, when adapter value is None)
        ssl_version=ssl.PROTOCOL_SSLv23
          accepts: None or a PROTOCOL_* enum loaded from OpenSSL
        cert_reqs=ssl.CERT_REQUIRED
          accepts: None or one of CERT_NONE, CERT_OPTIONAL, CERT_REQUIRED
        options=ssl.OP_NO_SSLv2 | ssl.OP_NO_SSLv3 | ssl.OP_NO_COMPRESSION
          accepts: None or ssl.OP_* client-side enums loaded from OpenSSL
        ciphers=urllib3.util.ssl_.DEFAULT_CIPHERS
          accepts: None or string of OpenSSL ciphers
          see: https://wiki.openssl.org/index.php/Manual:Ciphers(1)
               and (https://www.openssl.org/docs/man1.0.2/apps/ciphers.html
               or https://www.openssl.org/docs/man1.1.0/apps/ciphers.html)

    :param context_options: ssl.context options, accepts any:
        cafile=None
          accepts: None or path to contatenated PEM file of CAs
        certfile=None
          accepts: None or path to PEM file of client cert (with no key)
        keyfile=None
          accepts: None or path to PEM file of client cert key (path required
                   if certfile path defined)
        password=None
          accepts: None or password string

    :param adapter_options: HTTPAdapter options defaults, accepts any:
        https_retries=3
          accepts: None, int >= 0 or False
          (0 does not retry; False does the same, but skips rasising)
        https_redirects=3
          accepts: None, int >= 0 or False
          (0 does not redirect; False does the same, but skips rasising)
    """
    def __init__(self, context_create_options, context_options,
                 adapter_options, *args, **kwargs):
        self._ctx_create_opts = context_create_options
        self._ctx_opts = context_options
        self._adptr_opts = adapter_options

        # set up adapter options
        retries = self._adptr_opts.get('retries', None)
        redirects = self._adptr_opts.get('redirects', None)
        if retries is not None:  # needs int; redirects can be None
            kwargs['max_retries'] = Retry(total=retries, redirect=redirects)

        super(SslContextAdapter, self).__init__(*args, **kwargs)

    @staticmethod
    def normalize_hostname(url):
        """
        Replace url with same URL, but with lowercased hostname
        :param url: A URL
        :rtype: basestring
        """
        parts = urlparse(url)
        return re.sub(parts.hostname, parts.hostname, url, count=1, flags=re.I)

    def update_context(self, context):
        """
        :type context: ssl.SSLContext
        """
        cafile = self._ctx_opts.get('cafile', None)
        if cafile:
            context.load_verify_locations(cafile=cafile)
        else:
            # TODO: Will loaded defaults be overridden later by socket wrap?
            context.load_default_certs(purpose=Purpose.SERVER_AUTH)

        certfile = self._ctx_opts.get('certfile', None)
        keyfile = self._ctx_opts.get('keyfile', None)
        password = self._ctx_opts.get('password', None)
        supports_password = True
        if certfile and keyfile:
            try:
                context.load_cert_chain(certfile=certfile,
                                        keyfile=keyfile,
                                        password=password)
            except TypeError:
                # urllib3.create_urllib3_context() (as of v1.22) and older ssl
                # modules do not support setting a private key password.
                # However, we can't use inspect to test for the kwarg, because
                # load_cert_chain is a built-in method bound to OpenSSL lib.
                context.load_cert_chain(certfile=certfile,
                                        keyfile=keyfile)
                supports_password = False

        if not supports_password and password is not None:
            raise SSLError('Private key password defined, but underlying SSL '
                           'context does not support setting it')

    def init_poolmanager(self, *args, **kwargs):
        context = create_urllib3_context(**self._ctx_create_opts)
        self.update_context(context)
        kwargs['ssl_context'] = context
        return super(SslContextAdapter, self).init_poolmanager(*args,
                                                               **kwargs)

    def proxy_manager_for(self, *args, **kwargs):
        context = create_urllib3_context(**self._ctx_create_opts)
        self.update_context(context)
        kwargs['ssl_context'] = context
        return super(SslContextAdapter, self).proxy_manager_for(*args,
                                                                **kwargs)

    # **kwargs doesn't work here; requests' send() calls 'proxies' positionally
    def get_connection(self, url, proxies=None):
        url = self.normalize_hostname(url)
        return super(SslContextAdapter, self).get_connection(url,
                                                             proxies=proxies)

    def request_url(self, request, proxies):
        request.url = self.normalize_hostname(request.url)
        return super(SslContextAdapter, self).request_url(request, proxies)

    def send(self, request, **kwargs):
        request.url = self.normalize_hostname(request.url)
        return super(SslContextAdapter, self).send(request, **kwargs)


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


def get_ssl_config_map():
    # TODO: Add ssl_config_map model query, returning dict like SSL_CONFIG_MAP
    # SSL_CONFIG_MAP is a dict representation of ssl_config_map model records
    return SSL_CONFIG_MAP


def get_ssl_configs():
    # TODO: Add ssl_config model query, returning dict like SSL_CONFIGS
    # SSL_CONFIGS is a dict representation of ssl_config model records
    return SSL_CONFIGS


def get_ssl_context_opts(url):
    """
    :param url: URL or base URL, e.g. https://mydomain:8000
    :type url: basestring
    :return: tuple of dicts that matches input for SslContextAdapter
    """

    config_map = get_ssl_config_map()
    configs = get_ssl_configs()

    ssl_config = dict(SSL_DEFAULT_CONFIG)
    """:type: SSL_DEFAULT_CONFIG"""

    host_port = hostname_port(url)  # MUST to be lowercase
    if host_port in config_map:
        config_id = config_map[host_port]
        if config_id in configs:
            ssl_config.update(configs[config_id])
        else:
            raise KeyError(
                'SSL config of ID {0} not found'.format(config_id))

    # print(ssl_config)

    if not isinstance(ssl_config, dict):
        raise TypeError("SSL config not defined as dictionary")
    if 'name' not in ssl_config:
        raise KeyError("SSL config does not have a name property")

    # SslContextAdapter context_create_options
    ctx_c_opts = dict()
    ctx_c_opts['ssl_version'] = \
        resolve_ssl_version(ssl_config.get('ssl_version', None))
    ctx_c_opts['cert_reqs'] = \
        resolve_cert_reqs(ssl_config.get('ssl_verify_mode', None))
    ssl_opts = ssl_config.get('ssl_options', None)
    opts = 0
    if ssl_opts and isinstance(ssl_opts, list):
        # ssl OP_* enums are dynamically loaded from OpenSSL, so verify
        # they are present in ssl module before bitwise appending them
        op_opts = [o for o in dir(ssl) if o.startswith('OP_')]
        for opt in ssl_opts:
            if opt in op_opts:
                opts |= getattr(ssl, opt)
            else:
                # TODO: Log (don't raise) unresolvable options, for admin
                pass
    ctx_c_opts['options'] = opts if opts else None
    ctx_c_opts['ciphers'] = ssl_config.get('ssl_ciphers', None)

    # SslContextAdapter context_options
    ctx_opts = dict()
    ctx_opts['cafile'] = ssl_config.get('ca_custom_certs', None)
    ctx_opts['certfile'] = ssl_config.get('client_cert', None)
    ctx_opts['keyfile'] = ssl_config.get('client_key', None)
    ctx_opts['password'] = ssl_config.get('client_key_pass', None)

    # SslContextAdapter adapter_options
    adptr_opts = dict()
    adptr_opts['retries'] = ssl_config.get('https_retries', None)
    adptr_opts['redirects'] = ssl_config.get('https_redirects', None)

    return ctx_c_opts, ctx_opts, adptr_opts
