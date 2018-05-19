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

import ssl
import re
import logging
import warnings

from collections import OrderedDict
from fnmatch import fnmatch

from ordered_model.models import OrderedModel
from django.conf import settings
from django.db import models
from django.db.utils import OperationalError
from django.core.exceptions import ValidationError

from .settings import get_pki_dir, CERT_MATCH, KEY_MATCH, SSL_DEFAULT_CONFIG
from .utils import hostname_port as filter_hostname_port
from .utils import file_readable, pki_file, relative_to_absolute_url
from .fields import EncryptedCharField, DynamicFilePathField
from .validate import (
    PkiValidationError,
    PkiValidationWarning,
    validate_cert_file_matches_key_file,
    validate_ca_certs,
    validate_client_cert,
    validate_client_key,
)

logger = logging.getLogger(__name__)

# Global mirror cache of mapping patterns for HostnamePortSslConfig records
hostnameport_pattern_cache = list()
hostnameport_pattern_cache_built = False

# Global cache of mapping patterns that also have proxy enabled
hostnameport_pattern_proxy_cache = list()


def hostnameport_patterns(uses_proxy=None):
    """
    :param uses_proxy: Filter by whether connections should require
    routing through internal proxy or not. 'None' indicates no filtering.
    :rtype: list
    """
    return HostnamePortSslConfig.objects.hostnameport_patterns(
        uses_proxy=uses_proxy)


def rebuild_hostnameport_pattern_cache():
    global hostnameport_pattern_cache_built
    del hostnameport_pattern_cache[:]
    del hostnameport_pattern_proxy_cache[:]
    try:
        hostnameport_pattern_cache.extend(
            hostnameport_patterns()
        )
        hostnameport_pattern_proxy_cache.extend(
            hostnameport_patterns(uses_proxy=True)
        )
        hostnameport_pattern_cache_built = True
        logger.debug(u'hostnameport_pattern_cache rebuilt: {0}'
                     .format(hostnameport_pattern_cache))
        logger.debug(u'hostnameport_pattern_proxy_cache rebuilt: {0}'
                     .format(hostnameport_pattern_proxy_cache))
    except OperationalError:
        # skip if db isn't initialized yet
        logger.debug('hostnameport pattern caches FAILED to rebuild')
        pass


def hostnameport_pattern_for_url(
        url, via_query=False, uses_proxy=None, scheme='https'):
    url = relative_to_absolute_url(url, scheme=scheme)
    if not url.lower().startswith('https'):
        return None
    if via_query or not hostnameport_pattern_cache_built:
        rebuild_hostnameport_pattern_cache()
    if uses_proxy is not None and isinstance(uses_proxy, bool):
        if uses_proxy:
            ptrn_cache = hostnameport_pattern_proxy_cache
        else:
            ptrn_cache = [p for p in hostnameport_pattern_cache
                          if p not in hostnameport_pattern_proxy_cache]
        proxy_txt = 'proxy '
    else:
        ptrn_cache = hostnameport_pattern_cache
        proxy_txt = ''

    for ptn in ptrn_cache:
        if fnmatch(filter_hostname_port(url), ptn):
            logger.debug(u"URL matches hostname:port {0}pattern: {1} > '{2}'"
                         .format(proxy_txt, url, ptn))
            return ptn

    logger.debug(u'URL does not match any hostname:port {0}patterns: {1}'
                 .format(proxy_txt, url))
    logger.debug(u'Current hostnameport_pattern_cache: {0}'
                 .format(hostnameport_pattern_cache))
    logger.debug(u'Current hostnameport_pattern_proxy_cache: {0}'
                 .format(hostnameport_pattern_proxy_cache))
    return None


def has_ssl_config(url, via_query=False, scheme='https'):
    """
    Checks whether a URL matches a pattern in the cache.

    Note: To check if external proxying is needed, use
    :func:`uses_proxy_route` instead.

    :param url: Any URL, with an https scheme.
    :param via_query: Whether to rebuild the pattern cache first, via db query.
    :param scheme: See utils.protocol_relative_to_scheme
    :rtype: bool
    """
    url = relative_to_absolute_url(url, scheme=scheme)
    if not url.lower().startswith('https'):
        return False
    ptn = hostnameport_pattern_for_url(url, via_query=via_query)
    if ptn is not None:
        return True
    return False


def ssl_config_for_url(url, uses_proxy=None, scheme='https'):
    """
    Find an SslConfig for a URL.
    Fix any missing related SslConfig by reverting to default.
    :param url:
    :param uses_proxy: Filter by whether connections should require
    routing through internal proxy or not. 'None' indicates no filtering.
    :param scheme: See utils.protocol_relative_to_scheme
    :rtype: SslConfig | None
    """
    url = relative_to_absolute_url(url, scheme=scheme)
    if not url.lower().startswith('https'):
        return None

    ssl_config = None

    ptn = hostnameport_pattern_for_url(
        url, via_query=True, uses_proxy=uses_proxy)
    if ptn is not None:
        # this get should not fail or return duplicates
        mp = HostnamePortSslConfig.objects.get(hostname_port=ptn)
        HostnamePortSslConfig.objects.ensure_ssl_config(mp)
        ssl_config = mp.ssl_config

    return ssl_config


def uses_proxy_route(url, via_query=False, scheme='https'):
    """
    Checks whether a URL matches a pattern in the cache, taking into account
    whether mapping also uses an external proxy through this application.

    This also indicates that the hostnameport pattern is effectively included
    in settings.PROXY_ALLOWED_HOSTS.

    Note: To check if URL just matches a mapping, i.e. has an SslConfig, use
    :func:`has_ssl_config` instead.

    :param url: Any URL, with an https scheme.
    :param via_query: Whether to rebuild the pattern cache first, via db query.
    :param scheme: See utils.protocol_relative_to_scheme
    :rtype: bool
    """
    url = relative_to_absolute_url(url, scheme=scheme)
    if not url.lower().startswith('https'):
        return False

    # No need to proxy a local GeoServer
    if (url.startswith(settings.GEOSERVER_URL.rstrip('/')) and
            settings.GEOSERVER_URL.startswith(settings.SITEURL.rstrip('/'))):
        return False

    ptn = hostnameport_pattern_for_url(
        url, via_query=via_query, uses_proxy=True)
    if ptn is not None:
        return True
    return False


class SslConfigManager(models.Manager):

    def create_default(self):
        try:
            self.get(pk=1)
        except SslConfig.DoesNotExist:
            config = SSL_DEFAULT_CONFIG
            config['pk'] = 1
            self.create(**config)

    def get_create_default(self):
        self.create_default()
        return self.get(pk=1)

    def default_and_all(self):
        self.create_default()
        return self.all()


class SslConfig(models.Model):
    # _ssl_versions = [
    #     v for v in dir(ssl) if v.startswith('PROTOCOL_')
    # ]
    # TLS is removed since it was just introduced in 2.7.13
    _ssl_versions = [
        ('PROTOCOL_SSLv23', 'SSLv23 (SSLv3, SSLv23, TLSv1, TLSv1.1, TLSv1.2)'),
        ('PROTOCOL_SSLv3', 'SSLv3 (SSLv3, SSLv23)'),
        ('PROTOCOL_TLSv1', 'TLSv1 (SSLv23, TLSv1)'),
        ('PROTOCOL_TLSv1_1', 'TLSv1.1 (SSLv23, TLSv1.1)'),
        ('PROTOCOL_TLSv1_2', 'TLSv1.2 (SSLv23, TLSv1.2)'),
    ]
    # Default as of Python 2.7.14 (Py3 is 'TLS')
    _ssl_version_default = 'PROTOCOL_SSLv23'
    # _ssl_verify_modes = [
    #     m for m in dir(ssl) if m.startswith('CERT_')
    # ]
    _ssl_verify_modes = [
        ('CERT_NONE', 'CERT NONE'),
        ('CERT_OPTIONAL', 'CERT OPTIONAL'),
        ('CERT_REQUIRED', 'CERT REQUIRED'),
    ]
    # _ssl_options = [
    #     o for o in dir(ssl) if o.startswith('OP_')
    # ]
    # OP_NO_TLSv1_3 is removed since it was just introduced in 2.7.15, and
    # it requires use of PROTOCOL_TLS (introduced in 2.7.13)
    _ssl_options = [
        'OP_ALL',
        'OP_CIPHER_SERVER_PREFERENCE',
        'OP_NO_COMPRESSION',
        'OP_NO_SSLv2',
        'OP_NO_SSLv3',
        'OP_NO_TLSv1',
        'OP_NO_TLSv1_1',
        'OP_NO_TLSv1_2',
        'OP_SINGLE_DH_USE',
        'OP_SINGLE_ECDH_USE',
    ]
    _redos = [(str(x), str(x)) for x in (range(11) + [False])]

    name = models.CharField(
        "Name",
        max_length=128,
        blank=False,
        help_text="(REQUIRED) Display name of configuration.",
    )
    description = models.TextField(
        "Description",
        blank=True,
        help_text="(Optional) Details about configuration for user.",
    )
    ca_custom_certs = DynamicFilePathField(
        "Custom CA cert file",
        path=get_pki_dir,
        match=CERT_MATCH,
        blank=True,
        help_text="(Optional) Certificate of concatenated Certificate "
                  "Authorities, in PEM format. "
                  "If undefined, System (via OpenSSL) CAs are used.",
    )
    ca_allow_invalid_certs = models.BooleanField(
        "Allow invalid CAs",
        # choices=_allow_invalid,
        default=False,
        blank=False,
        help_text="(Optional) Used during pre-validation of SSL components in "
                  "a config. NOTE: this does not mean OpenSSL will accept any "
                  "invalid certificates.",
    )
    client_cert = DynamicFilePathField(
        "Client certificate file",
        path=get_pki_dir,
        match=CERT_MATCH,
        blank=True,
        help_text="(Optional) Client certificate in PEM format. "
                  "REQUIRED if client_key is defined. "
                  "Client certs that also contain keys are not supported.",
    )
    client_key = DynamicFilePathField(
        "Client cert private key file",
        path=get_pki_dir,
        match=KEY_MATCH,
        blank=True,
        help_text="(Optional) Client certificate's private key in PEM format. "
                  "REQUIRED if client_cert is defined. "
                  "It is highly recommended the key be password-encrypted.",
    )
    # TODO: update ^ text with 'unless .p12|.pfx cert defined'
    # Password limited to 100 characters, otherwise encrypted result's length
    # may exceed 255 character field limit
    client_key_pass = EncryptedCharField(
        "Client cert private key password",
        max_length=255,
        blank=True,
        help_text="(Optional) Client certificate's private key password. "
                  "Limited to 100 characters.",
    )
    # TODO: update ^ text with 'Required if .p12|.pfx cert defined'
    ssl_version = models.CharField(
        "SSL version",
        max_length=18,
        choices=_ssl_versions,
        default='PROTOCOL_SSLv23',
        blank=False,
        help_text="Supported SSL/TLS Protocol to use. Unless a specific "
                  "version of TLS is required, it is recommended to set this "
                  "to SSLv23 (which supports all stable TLS versions), then "
                  "add ssl_options to remove any unwanted protocols. See ssl "
                  "PROTOCOL_* constant documentation for details: "
                  "https://docs.python.org/2/library/ssl.html",
    )
    ssl_verify_mode = models.CharField(
        "SSL peer verify mode",
        max_length=16,
        choices=_ssl_verify_modes,
        default='CERT_REQUIRED',
        blank=False,
        help_text="How to handle verification of peer certificates (e.g. from "
                  "endpoints). Setting to anything other than REQUIRED is not "
                  "advised. See ssl CERT_* constant documentation for details:"
                  " https://docs.python.org/2/library/ssl.html",
    )
    ssl_options = models.CharField(
        "SSL options",
        max_length=255,
        blank=True,
        help_text="(Optional) Comma-separated list of SSL module options. "
                  "If undefined, defaults to "
                  "'OP_NO_SSLv2, OP_NO_SSLv3, OP_NO_COMPRESSION'. "
                  "See ssl OP_* constant documentation for details: "
                  "https://docs.python.org/2/library/ssl.html",
    )
    ssl_ciphers = models.TextField(
        "SSL ciphers",
        blank=True,
        help_text="(Optional) OpenSSL string of supported ciphers. Note these "
                  "may be ignored if ssl_options 'CIPHER_SERVER_PREFERENCE' "
                  "is set or the endpoint requires its ciphers be used. "
                  "See: https://wiki.openssl.org/index.php/Manual:Ciphers(1)",
    )
    https_retries = models.CharField(
        "Retry failed requests",
        max_length=6,
        choices=_redos,
        default='3',
        blank=False,
        help_text="Number of connection retries to attempt. Value of 0 does "
                  "not retry; False does the same, but skips raising an "
                  "error.",
    )
    https_redirects = models.CharField(
        "Follow request redirects",
        max_length=6,
        choices=_redos,
        default='3',
        blank=False,
        help_text="Number of connection redirects to follow. Value of 0 does "
                  "not follow any; False does the same, but skips raising an "
                  "error.",
    )

    objects = SslConfigManager()

    def __str__(self):
        return self.name

    @staticmethod
    def ssl_op_opts():
        """Runtime collection of available ssl module OP_* constants"""
        return [o for o in dir(ssl) if o.startswith('OP_')]

    @staticmethod
    def ssl_protocols():
        """Runtime collection of available ssl module PROTOCOL_* constants"""
        return [p for p in dir(ssl) if p.startswith('PROTOCOL_')]

    def clean(self):
        # Validators
        val_mgs = {}

        if self.ssl_options:
            opts = self.ssl_options.replace(' ', '').split(',')
            # print(opts)
            invalid_opts = []
            for opt in opts:
                if opt and opt not in self.ssl_op_opts():
                    invalid_opts.append(opt)
            if invalid_opts:
                    msg = "Options {0} not in ssl module options: [{1}]"\
                          .format(', '.join(invalid_opts),
                                  ','.join(self.ssl_op_opts()))
                    val_mgs['ssl_options'] = msg

        # Make sure PKI components are readable
        for attr in ['ca_custom_certs', 'client_cert', 'client_key']:
            f = getattr(self, attr, None)
            if f and not file_readable(pki_file(f)):
                msg = 'File does not exist or not readable: {0}'.format(f)
                val_mgs[attr] = msg

        # TODO: update when .p12|.pfx cert support added
        #       client_key NOT needed for .p12|.pfx  client_cert
        #       client_key_pass needed for .p12|.pfx  client_cert
        if self.client_cert and not self.client_key:
            msg = 'Client key must be defined if client cert is.'
            val_mgs['client_key'] = msg
        if self.client_key and not self.client_cert:
            msg = 'Client cert must be defined if client key is.'
            val_mgs['client_cert'] = msg

        if self.client_key_pass and len(self.client_key_pass) > 100:
            msg = 'Client key password limited to 100 characters.'
            val_mgs['client_key_pass'] = msg

        # Validate supplied PKI components
        warn_msgs = []
        if self.ca_custom_certs:
            try:
                warns = validate_ca_certs(
                    self.ca_custom_certs,
                    allow_expired=self.ca_allow_invalid_certs
                )
                warn_msgs.extend(warns)
            except PkiValidationError as e:
                val_mgs['ca_custom_certs'] = e.message_html()

        if self.client_cert:
            try:
                warns = validate_client_cert(self.client_cert)
                warn_msgs.extend(warns)
            except PkiValidationError as e:
                val_mgs['client_cert'] = e.message_html()

        if self.client_key:
            try:
                warns = validate_client_key(
                    self.client_key,
                    password=self.client_key_pass.strip()
                )
                warn_msgs.extend(warns)
            except PkiValidationError as e:
                val_mgs['client_key'] = e.message_html()

            try:
                warns = validate_cert_file_matches_key_file(
                    self.client_cert,
                    self.client_key,
                    self.client_key_pass
                )
                warn_msgs.extend(warns)
            except PkiValidationError as e:
                val_mgs['client_key'] = e.message_html()

        if val_mgs:
            raise ValidationError(val_mgs)

        if warn_msgs:
            warnings.warn(PkiValidationWarning(warn_msgs))

    @staticmethod
    def default_ssl_config():
        ssl_config = SslConfig(**SSL_DEFAULT_CONFIG)
        ssl_config.pk = 1
        return ssl_config

    def to_dict(self):
        """Dump model values to dict like pki.settings.SSL_DEFAULT_CONFIG"""
        ssl_opts = self.ssl_options.replace(' ', '').split(',') \
            if self.ssl_options else None
        return {
            "name": self.name,
            "ca_custom_certs":
                self.ca_custom_certs if self.ca_custom_certs else None,
            "ca_allow_invalid_certs": bool(self.ca_allow_invalid_certs),
            "client_cert":
                self.client_cert if self.client_cert else None,
            "client_key":
                self.client_key if self.client_key else None,
            "client_key_pass": self.client_key_pass or None,
            "ssl_version":
                str(self.ssl_version)
                if str(self.ssl_version) in self.ssl_protocols()
                else self._ssl_version_default,
            "ssl_verify_mode": str(self.ssl_verify_mode),
            "ssl_options":
                [str(o) for o in ssl_opts if str(o) in self.ssl_op_opts()]
                if ssl_opts else None,
            "ssl_ciphers": str(self.ssl_ciphers) or None,
            "https_retries": str(self.https_retries) or None,
            "https_redirects": str(self.https_redirects) or None,
        }

    class Meta:
        verbose_name = 'SSL Config'
        verbose_name_plural = 'SSL Configs'


class HostnamePortSslConfigManager(models.Manager):

    def create_hostnameportsslconfig(self, ptn, ssl_config):
        """
        Instantiates a new HostnamePortSslConfig.
        :param ssl_config: SslConfig instance, already saved in table
        :type ssl_config: SslConfig
        :param ptn: Pattern to match URLs
        :type ptn: str | unicode
        :return: new HostnamePortSslConfig
        :rtype: HostnamePortSslConfig
        """
        # Raise ValidationError because creation is result of form submission
        if not ssl_config or not isinstance(ssl_config, SslConfig):
            raise ValidationError(
                'SslConfig for hostname:port mapping is undefined.')
        if ssl_config.pk is None:
            raise ValidationError(
                "SslConfig for hostname:port mapping is not saved in table.")

        try:
            service_hostnameportsslconfig = self.get(hostname_port=ptn)
            if not service_hostnameportsslconfig.ssl_config:
                # something went pear-shaped with record's SslConfig; nix it
                service_hostnameportsslconfig.delete()
                raise HostnamePortSslConfig.DoesNotExist
            service_hostnameportsslconfig.ssl_config = ssl_config
            service_hostnameportsslconfig.save()
        except HostnamePortSslConfig.DoesNotExist:
            service_hostnameportsslconfig = self.create(
                hostname_port=ptn,
                ssl_config=ssl_config
            )

        return service_hostnameportsslconfig

    @staticmethod
    def ensure_ssl_config(mp):
        hnp = mp.hostname_port
        logger.debug(u"Fetching SslConfig related record, "
                     u"for hostname:port pattern: {0}".format(hnp))
        config = mp.ssl_config
        if config and isinstance(config, SslConfig):
            logger.debug("Found SslConfig related record: {0}"
                         .format(config.to_dict()
                                 .get('name', '(name missing)')))
        else:
            logger.warn("Missing SslConfig related record, "
                        "reverting to default")
            mp.ssl_config = SslConfig.objects.get_create_default()
            mp.save()

    def hostnameport_patterns(self, uses_proxy=None):
        """
        Return enabled hostname:port mapping patterns (and optionally filter).
        Ensures hostname:port matching is done in user-defined order.
        :param uses_proxy: Filter by whether connections should require
        routing through internal proxy or not. 'None' indicates no filtering.
        :rtype: list
        """
        kwargs = {'enabled': True}
        if uses_proxy is not None:
            kwargs['proxy'] = bool(uses_proxy)
        q_set = self.filter(**kwargs).order_by('order')\
            .values_list('hostname_port', flat=True)
        return list(q_set)

    def mapped_ssl_configs(self):
        """
        Return all mappings as an ordered dictionary.
        Ensures hostname:port matching is done in user-defined order.

        Fix any missing related SslConfigs by reverting to default.
        :return:
        :rtype: OrderedDict
        """
        q_set = self.filter(enabled=True).order_by('order')
        mapped_configs = OrderedDict()
        for mp in q_set:
            self.ensure_ssl_config(mp)
            mapped_configs[mp.hostname_port] = mp.ssl_config
        return mapped_configs


class HostnamePortSslConfig(OrderedModel):
    enabled = models.BooleanField(
        "Enabled",
        default=True,
        blank=False,
        help_text="Whether mapping is enabled",
    )
    hostname_port = models.CharField(
        "Hostname:Port",
        max_length=255,
        blank=False,
        primary_key=True,
        unique=True,
        help_text="(REQUIRED) Hostname and (optional) port. "
                  "MUST be all lowercase.<br/><br/>"
                  "Examples:<br/>"
                  "<b>mydomain.com</b><br/><b>mydomain.com:8000</b><br/><br/>"
                  "Wildcard '*' character matching is supported "
                  "(use sparingly)."
                  "<br/><br/>Examples:<br/>"
                  "<b>*.mydomain.com</b> (matches subdomains)<br/>"
                  "<b>*.mydomain.com*</b> (matches subdomains and all ports)"
                  "<br/><b>*.*</b> "
                  "(matches ALL https requests; avoid unless necessary)"
                  "<br/><br/>"
                  "<em>Use admin list view to sort patterns for matching.</em>"
    )
    ssl_config = models.ForeignKey(
        SslConfig,
        verbose_name='Ssl config',
        related_name='+',
        null=True,
    )
    proxy = models.BooleanField(
        "Proxy",
        default=True,
        blank=False,
        help_text="Whether to require client's browser connections to be "
                  "proxied through this application.",
    )
    objects = HostnamePortSslConfigManager()

    def __str__(self):
        return "{0} -> SSL config: {1}".format(self.hostname_port,
                                               self.ssl_config)

    def clean(self):
        # Validators
        val_mgs = {}
        if self.hostname_port.lower() != self.hostname_port:
            msg = "Hostname must be all lowercase."
            val_mgs['hostname_port'] = msg

        # Validate hostname:port with wildcard notation
        # TODO: Matches unicode alphanumeric for international domain names,
        #       but not symbol code points, which is probably an edge case.
        #       Not sure how to do this in Py2 (maybe regex package?)
        p_domain_char = re.compile('[-.\w:*]', re.IGNORECASE | re.UNICODE)
        if not all([p_domain_char.match(c.encode('UTF-8'))
                    for c in self.hostname_port]):
            msg = u'Invalid characters in hostname:port definition: {0}' \
                .format(self.hostname_port)
            val_mgs['hostname_port'] = msg

        if val_mgs:
            raise ValidationError(val_mgs)

    class Meta(OrderedModel.Meta):
        verbose_name = 'Hostname:Port >> SSL Config'
        verbose_name_plural = 'Hostname:Port >> SSL Configs'
        # ordering = ["hostname_port"]  # now handled by OrderedModel
        unique_together = (("hostname_port", "ssl_config"),)
