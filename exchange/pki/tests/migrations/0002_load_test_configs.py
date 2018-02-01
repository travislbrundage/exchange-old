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

import os
from django.db import migrations

TEST_FILES = os.path.join(
    os.path.dirname(os.path.dirname(os.path.realpath(__file__))),
    'files'
)


def load_configs(apps, _):  # unused schema_editor param
    sslconfig = apps.get_model('pki', 'SslConfig')

    ssl_configs = [
        dict(
            name='Just custom CAs',
            ca_custom_certs='{0}/root-root2-chains.pem'.format(TEST_FILES),
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
            ca_custom_certs='{0}/root-root2-chains.pem'.format(TEST_FILES),
            ca_allow_invalid_certs=False,
            client_cert='{0}/alice-cert.pem'.format(TEST_FILES),
            client_key='{0}/alice-key.pem'.format(TEST_FILES),
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
            ca_custom_certs='{0}/root-root2-chains.pem'.format(TEST_FILES),
            ca_allow_invalid_certs=False,
            client_cert='{0}/alice-cert.pem'.format(TEST_FILES),
            client_key='{0}/alice-key_w-pass.pem'.format(TEST_FILES),
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
            ca_custom_certs='{0}/root-root2-chains.pem'.format(TEST_FILES),
            ca_allow_invalid_certs=False,
            client_cert='{0}/jane-cert.pem'.format(TEST_FILES),
            client_key='{0}/jane-key_w-pass.pem'.format(TEST_FILES),
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
            ca_custom_certs='{0}/root-root2-chains.pem'.format(TEST_FILES),
            ca_allow_invalid_certs=False,
            client_cert='{0}/alice-cert.pem'.format(TEST_FILES),
            client_key='{0}/alice-key_w-pass.pem'.format(TEST_FILES),
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
            ca_custom_certs='{0}/root-root2-chains.pem'.format(TEST_FILES),
            ca_allow_invalid_certs=False,
            client_cert='{0}/alice-cert.pem'.format(TEST_FILES),
            client_key='{0}/alice-key.pem'.format(TEST_FILES),
            client_key_pass='password',
            ssl_version="PROTOCOL_TLSv1_2",
            ssl_verify_mode="CERT_NONE",
            ssl_options='',
            ssl_ciphers='',
            https_retries="3",
            https_redirects="3",
        ),
        dict(
            name='PKI: key with no password; TLSv1_2-only (via ssl_options)',
            ca_custom_certs='{0}/root-root2-chains.pem'.format(TEST_FILES),
            ca_allow_invalid_certs=False,
            client_cert='{0}/alice-cert.pem'.format(TEST_FILES),
            client_key='{0}/alice-key.pem'.format(TEST_FILES),
            client_key_pass='password',
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
        ('pki', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(load_configs, delete_configs),
    ]
