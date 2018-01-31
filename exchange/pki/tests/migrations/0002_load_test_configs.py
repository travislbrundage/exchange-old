# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import os
from django.db import migrations

TEST_FILES = os.path.join(
    os.path.dirname(os.path.dirname(os.path.realpath(__file__))),
    'files'
)


# noinspection PyCallingNonCallable
def load_configs(apps, _):  # unused schema_editor param
    sslconfig = apps.get_model('pki', 'SslConfig')  # type: SslConfig

    config1 = sslconfig(
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
    )
    config1.save()

    config2 = sslconfig(
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
    )
    config2.save()

    config3 = sslconfig(
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
    )
    config3.save()

    config4 = sslconfig(
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
    )
    config4.save()

    config5 = sslconfig(
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
    )
    config5.save()

    config6 = sslconfig(
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
    )
    config6.save()

    config7 = sslconfig(
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
    )
    config7.save()


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
