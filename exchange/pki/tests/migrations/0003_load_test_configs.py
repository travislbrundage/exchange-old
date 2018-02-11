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

from __future__ import unicode_literals

from django.db import migrations


def load_configs(apps, _):  # unused schema_editor param
    sslconfig = apps.get_model('pki', 'SslConfig')

    ssl_configs = [
        dict(
            name='Just custom CAs',
            description='',
            ca_custom_certs='root-root2-chains.pem',
            ca_allow_invalid_certs=False,
            client_cert='',
            client_key='',
            client_key_pass='',
            ssl_version="PROTOCOL_SSLv23",
            ssl_verify_mode="CERT_REQUIRED",
            ssl_options='',
            ssl_ciphers='',
            https_retries="3",
            https_redirects="3",
        ),
        dict(
            name='PKI: key with no password',
            description='',
            ca_custom_certs='root-root2-chains.pem',
            ca_allow_invalid_certs=False,
            client_cert='alice-cert.pem',
            client_key='alice-key.pem',
            client_key_pass='',
            ssl_version="PROTOCOL_SSLv23",
            ssl_verify_mode="CERT_REQUIRED",
            ssl_options='',
            ssl_ciphers='',
            https_retries="3",
            https_redirects="3",
        ),
        dict(
            name='PKI: key with password',
            description='',
            ca_custom_certs='root-root2-chains.pem',
            ca_allow_invalid_certs=False,
            client_cert='alice-cert.pem',
            client_key='alice-key_w-pass.pem',
            client_key_pass='password',
            ssl_version="PROTOCOL_SSLv23",
            ssl_verify_mode="CERT_REQUIRED",
            ssl_options='',
            ssl_ciphers='',
            https_retries="3",
            https_redirects="3",
        ),
        dict(
            name='PKI: key with password; TLSv1_2-only; alt root CA chain',
            description='',
            ca_custom_certs='root-root2-chains.pem',
            ca_allow_invalid_certs=False,
            client_cert='jane-cert.pem',
            client_key='jane-key_w-pass.pem',
            client_key_pass='password',
            ssl_version="PROTOCOL_SSLv23",
            ssl_verify_mode="CERT_REQUIRED",
            ssl_options='',
            ssl_ciphers='',
            https_retries="3",
            https_redirects="3",
        ),
        dict(
            name='PKI: key with password; TLSv1_2-only',
            description='',
            ca_custom_certs='root-root2-chains.pem',
            ca_allow_invalid_certs=False,
            client_cert='alice-cert.pem',
            client_key='alice-key_w-pass.pem',
            client_key_pass='password',
            ssl_version="PROTOCOL_TLSv1_2",
            ssl_verify_mode="CERT_REQUIRED",
            ssl_options='',
            ssl_ciphers='',
            https_retries="3",
            https_redirects="3",
        ),
        dict(
            name='PKI: key with no password; custom CAs with no validation',
            description='',
            ca_custom_certs='root-root2-chains.pem',
            ca_allow_invalid_certs=False,
            client_cert='alice-cert.pem',
            client_key='alice-key.pem',
            client_key_pass='',
            ssl_version="PROTOCOL_TLSv1_2",
            ssl_verify_mode="CERT_NONE",
            ssl_options='',
            ssl_ciphers='',
            https_retries="3",
            https_redirects="3",
        ),
        dict(
            name='PKI: key with no password; TLSv1_2-only (via ssl_options)',
            description='',
            ca_custom_certs='root-root2-chains.pem',
            ca_allow_invalid_certs=False,
            client_cert='alice-cert.pem',
            client_key='alice-key.pem',
            client_key_pass='',
            ssl_version="PROTOCOL_SSLv23",
            ssl_verify_mode="CERT_REQUIRED",
            ssl_options='OP_NO_SSLv2, OP_NO_SSLv3, OP_NO_TLSv1, '
                        'OP_NO_TLSv1_1, OP_NO_COMPRESSION',
            ssl_ciphers='',
            https_retries="3",
            https_redirects="3",
        ),
    ]

    for config in ssl_configs:
        ssl_config = sslconfig(**config)
        # What the heck? This never calls model.clean() or any validations!
        ssl_config.full_clean()
        ssl_config.save()


def delete_configs(apps, _):  # unused schema_editor param
    sslconfig = apps.get_model('pki', 'SslConfig')
    sslconfig.objects.all().delete()


class Migration(migrations.Migration):

    dependencies = [
        ('pki', '0002_default_config'),
    ]

    operations = [
        migrations.RunPython(load_configs, delete_configs),
    ]
