# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='HostnamePortSslConfig',
            fields=[
                ('hostname_port', models.CharField(
                    max_length=255, unique=True, serialize=False,
                    verbose_name=b'Hostname:Port', primary_key=True)),
                ('ssl_config_id', models.IntegerField(
                    validators=[django.core.validators.MinValueValidator(1)])),
            ],
            options={
                'ordering': ['hostname_port'],
                'verbose_name': 'Hostname:Port to SSL Config Map',
                'verbose_name_plural': 'Hostname:Port to SSL Config Mappings',
            },
        ),
        migrations.CreateModel(
            name='SslConfig',
            fields=[
                ('id', models.AutoField(
                    verbose_name='ID', serialize=False, auto_created=True,
                    primary_key=True)),
                ('name', models.CharField(
                    help_text=b'(REQUIRED) Display name of config, shown in '
                              b'popup on remote services registration page '
                              b'and details page after registration.',
                    max_length=128, verbose_name=b'Name')),
                ('ca_custom_certs', models.FilePathField(
                    blank=True,
                    help_text=b"(Optional) Certificate of concatenated "
                              b"Certificate Authorities, from 'PKI_DIRECTORY' "
                              b"directory, in PEM format. If undefined, "
                              b"System (via OpenSSL) CAs are used.",
                    path=b'/usr/local/exchange-pki',
                    verbose_name=b'Custom CA cert file',
                    match=b'.*\\.(crt|CRT|pem|PEM)$')),
                ('ca_allow_invalid_certs', models.BooleanField(
                    default=False,
                    help_text=b'(Optional) Used during pre-validation of SSL '
                              b'components in a config. NOTE: this does not '
                              b'mean OpenSSL will accept any invalid '
                              b'certificates.',
                    verbose_name=b'Allow invalid CAs')),
                ('client_cert', models.FilePathField(
                    blank=True,
                    help_text=b"(Optional) Client certificate in PEM format, "
                              b"from 'PKI_DIRECTORY' directory. REQUIRED if "
                              b"client_key is defined. Client certs that "
                              b"also contain keys are not supported.",
                    path=b'/usr/local/exchange-pki',
                    verbose_name=b'Client certificate file',
                    match=b'.*\\.(crt|CRT|pem|PEM)$')),
                ('client_key', models.FilePathField(
                    blank=True,
                    help_text=b"(Optional) Client certificate's private key "
                              b"in PEM format, from 'PKI_DIRECTORY' "
                              b"directory. REQUIRED if client_cert is "
                              b"defined. It is highly recommended the key "
                              b"be password-encrypted.",
                    path=b'/usr/local/exchange-pki',
                    verbose_name=b'Client cert private key file',
                    match=b'.*\\.(key|KEY|pem|PEM)$')),
                ('client_key_pass', models.CharField(
                    help_text=b"(Optional) Client certificate's private "
                              b"key password.",
                    max_length=48,
                    verbose_name=b'Client cert private key password',
                    blank=True)),
                ('ssl_version', models.CharField(
                    default=b'PROTOCOL_SSLv23',
                    help_text=b'Supported SSL/TLS Protocol to use. Unless a '
                              b'specific version of TLS is required, it is '
                              b'recommended to set this to SSLv23 (which '
                              b'supports all stable TLS versions), then add '
                              b'ssl_options to remove any unwanted '
                              b'protocols. See ssl PROTOCOL_* constant '
                              b'docmentation for details: '
                              b'https://docs.python.org/2/library/ssl.html',
                    max_length=18,
                    verbose_name=b'SSL version',
                    choices=[
                        (b'PROTOCOL_SSLv23',
                         b'SSLv23 (SSLv3, SSLv23, TLSv1, TLSv1.1, TLSv1.2)'),
                        (b'PROTOCOL_SSLv3',
                         b'SSLv3 (SSLv3, SSLv23)'),
                        (b'PROTOCOL_TLSv1',
                         b'TLSv1 (SSLv23, TLSv1)'),
                        (b'PROTOCOL_TLSv1_1',
                         b'TLSv1.1 (SSLv23, TLSv1.1)'),
                        (b'PROTOCOL_TLSv1_2',
                         b'TLSv1.2 (SSLv23, TLSv1.2)')
                    ])),
                ('ssl_verify_mode', models.CharField(
                    default=b'CERT_REQUIRED',
                    help_text=b'How to handle verification of peer '
                              b'certificates (e.g. from endpoints). Setting '
                              b'to anything other than REQUIRED is '
                              b'notadvised. See ssl CERT_* constant '
                              b'docmentation for details: '
                              b'https://docs.python.org/2/library/ssl.html',
                    max_length=16, verbose_name=b'SSL peer verify mode',
                    choices=[(b'CERT_NONE', b'CERT NONE'),
                             (b'CERT_OPTIONAL', b'CERT OPTIONAL'),
                             (b'CERT_REQUIRED', b'CERT REQUIRED')])),
                ('ssl_options', models.CharField(
                    help_text=b"(Optional) Comman-separated list of SSL "
                              b"module options. If undefined, defaults to "
                              b"'OP_NO_SSLv2, OP_NO_SSLv, OP_NO_COMPRESSION'. "
                              b"See ssl OP_* constant docmentation for "
                              b"details: "
                              b"https://docs.python.org/2/library/ssl.html",
                    max_length=255, verbose_name=b'SSL options', blank=True)),
                ('ssl_ciphers', models.TextField(
                    help_text=b"(Optional) OpenSSL string of supported "
                              b"ciphers. Note these may be ignored if "
                              b"ssl_options 'CIPHER_SERVER_PREFERENCE' is "
                              b"set or the endpoint requires its ciphers be "
                              b"used. See: "
                              b"https://wiki.openssl.org/index.php/Manual:"
                              b"Ciphers(1)",
                    verbose_name=b'SSL ciphers', blank=True)),
                ('https_retries', models.CharField(
                    default=b'3',
                    help_text=b'Number of connection retries to attempt. '
                              b'Value of 0 does not retry; False does the '
                              b'same, but skips rasising an error.',
                    max_length=6, verbose_name=b'Retry failed requests',
                    choices=[(b'0', b'0'), (b'1', b'1'), (b'2', b'2'),
                             (b'3', b'3'), (b'4', b'4'), (b'5', b'5'),
                             (b'6', b'6'), (b'7', b'7'), (b'8', b'8'),
                             (b'9', b'9'), (b'10', b'10'),
                             (b'False', b'False')])),
                ('https_redirects', models.CharField(
                    default=b'3',
                    help_text=b'Number of connection redirects to follow. '
                              b'Value of 0 does not follow any; False does '
                              b'the same, but skips rasising an error.',
                    max_length=6, verbose_name=b'Follow request redirects',
                    choices=[(b'0', b'0'), (b'1', b'1'), (b'2', b'2'),
                             (b'3', b'3'), (b'4', b'4'), (b'5', b'5'),
                             (b'6', b'6'), (b'7', b'7'), (b'8', b'8'),
                             (b'9', b'9'), (b'10', b'10'),
                             (b'False', b'False')])),
            ],
            options={
                'verbose_name': 'SSL Config',
                'verbose_name_plural': 'SSL Configs',
            },
        ),
        migrations.AlterUniqueTogether(
            name='hostnameportsslconfig',
            unique_together=set([('hostname_port', 'ssl_config_id')]),
        ),
    ]