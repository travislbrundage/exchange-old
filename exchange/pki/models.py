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
import ssl
import logging

from django.db import models
from django.core.exceptions import ValidationError

logger = logging.getLogger(__name__)


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
    ca_custom_certs = models.CharField(
        "Custom CA cert file",
        max_length=255,
        blank=True,
        help_text="(Optional) Filesystem path to a certificate of "
                  "concatenated Certificate Authorities, in PEM format. "
                  "If undefined, System (via OpenSSL) CAs are used. "
                  "NOTE: should be outside of your application and www roots!",
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
    client_cert = models.CharField(
        "Client certificate file",
        max_length=255,
        blank=True,
        help_text="(Optional) Filesystem path to a client certificate in PEM "
                  "format. REQUIRED if client_key is defined. Client certs "
                  "that also contain keys are not supported. "
                  "NOTE: should be outside of your application and www roots!",
    )
    client_key = models.CharField(
        "Client cert private key file",
        max_length=255,
        blank=True,
        help_text="(Optional) Filesystem path to a client certificate's "
                  "private key in PEM format. REQUIRED if client_cert is "
                  "defined. It is highly recommended the key be "
                  "password-encrypted. "
                  "NOTE: should be outside of your application and www roots!",
    )
    # TODO: update ^ text with 'unless .p12|.pfx cert defined'
    client_key_pass = models.CharField(
        "Client cert private key password",
        max_length=48,
        blank=True,
        help_text="(Optional) Client certificate's private key password.",
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
                  "PROTOCOL_* constant docmentation for details: "
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
                  "advised. See ssl CERT_* constant docmentation for details: "
                  "https://docs.python.org/2/library/ssl.html",
    )
    ssl_options = models.CharField(
        "SSL options",
        max_length=255,
        blank=True,
        help_text="(Optional) Comman-separated list of SSL module options. "
                  "If undefined, defaults to "
                  "'OP_NO_SSLv2, OP_NO_SSLv, OP_NO_COMPRESSION'. "
                  "See ssl OP_* constant docmentation for details: "
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

    @staticmethod
    def _file_readable(a_file):
        return all([
            os.path.exists(a_file),
            os.path.isfile(a_file),
            os.access(a_file, os.R_OK)
        ])

    def clean(self):
        # Validators
        # TODO: Move these validation routines to a more common location,
        #       so they can be used for pre-validatin prior to connection

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
            if f and not self._file_readable(f):
                msg = 'File does not exist or not readable at: {0}'.format(f)
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

        if val_mgs:
            raise ValidationError(val_mgs)

        # TODO: validate supplied PKI components

    def to_ssl_config(self):
        """Dump model values to dict like pki.settings.SSL_DEFAULT_CONFIG"""
        ssl_opts = self.ssl_options.replace(' ', '').split(',') \
            if self.ssl_options else None
        return {
            "name": self.name,
            "ca_custom_certs": self.ca_custom_certs or None,
            "ca_allow_invalid_certs": bool(self.ca_allow_invalid_certs),
            "client_cert": self.client_cert or None,
            "client_key": self.client_key or None,
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


class HostnamePortSslConfig(models.Model):
    hostname_port = models.CharField(
        "Hostname:Port",
        max_length=255,
        blank=False,
        primary_key=True,
        unique=True,
        help_text="Hostname and (optional) port, e.g. 'mydomain.com' or "
                  "'mydomain.com:8000'. MUST be all lowercase."
    )
    ssl_config = models.ForeignKey(
        SslConfig,
        verbose_name='Ssl config',
        related_name='+',
        null=True,
    )

    def __str__(self):
        return "{0} -> SSL config: {1}".format(self.hostname_port,
                                               self.ssl_config)

    def clean(self):
        # Validators
        val_mgs = {}
        if self.hostname_port.lower() != self.hostname_port:
            msg = "Hostname must be all lowercase."
            val_mgs['hostname_port'] = msg

        if val_mgs:
            raise ValidationError(val_mgs)

    class Meta:
        verbose_name = 'Hostname:Port to SSL Config Map'
        verbose_name_plural = 'Hostname:Port to SSL Config Mappings'
        ordering = ["hostname_port"]
        unique_together = (("hostname_port", "ssl_config"),)
