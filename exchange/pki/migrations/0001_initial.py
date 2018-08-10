# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from ..fields import EncryptedCharField, DynamicFilePathField
from ..settings import get_pki_dir, CERT_MATCH, KEY_MATCH


class Migration(migrations.Migration):
    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='SslConfig',
            fields=[
                ('id', models.AutoField(
                    verbose_name='ID', serialize=False, auto_created=True,
                    primary_key=True)),
                ('name', models.CharField(
                    help_text=b'(REQUIRED) Display name of configuration.',
                    max_length=128, verbose_name=b'Name')),
                ('description', models.TextField(
                    help_text=b"(Optional) Details about configuration for "
                              b"user.",
                    verbose_name=b'Description', blank=True)),
                ('ca_custom_certs', DynamicFilePathField(
                    help_text=b'(Optional) Certificate of concatenated '
                              b'Certificate Authorities, in PEM format. '
                              b'If undefined, System '
                              b'(via OpenSSL) CAs are used.',
                    path=get_pki_dir,
                    match=CERT_MATCH,
                    verbose_name=b'Custom CA cert file',
                    blank=True)),
                ('ca_allow_invalid_certs', models.BooleanField(
                    default=False,
                    help_text=b'(Optional) Used during pre-validation of SSL '
                              b'components in a config. NOTE: this does not '
                              b'mean OpenSSL will accept any invalid '
                              b'certificates.',
                    verbose_name=b'Allow invalid CAs')),
                ('client_cert', DynamicFilePathField(
                    help_text=b'(Optional) Client certificate in PEM format. '
                              b'REQUIRED if client_key is defined. '
                              b'Client certs that also contain keys are not '
                              b'supported.',
                    path=get_pki_dir,
                    match=CERT_MATCH,
                    verbose_name=b'Client certificate file',
                    blank=True)),
                ('client_key', DynamicFilePathField(
                    help_text=b"(Optional) Client certificate's private key "
                              b"in PEM format. "
                              b"REQUIRED if client_cert is defined. "
                              b"It is highly recommended the key be "
                              b"password-encrypted.",
                    path=get_pki_dir,
                    match=KEY_MATCH,
                    verbose_name=b'Client cert private key file', blank=True)),
                ('client_key_pass', EncryptedCharField(
                    help_text=b"(Optional) Client certificate's private "
                              b"key password. Limited to 100 characters.",
                    max_length=255,
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
                              b'documentation for details: '
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
                              b'not advised. See ssl CERT_* constant '
                              b'documentation for details: '
                              b'https://docs.python.org/2/library/ssl.html',
                    max_length=16, verbose_name=b'SSL peer verify mode',
                    choices=[(b'CERT_NONE', b'CERT NONE'),
                             (b'CERT_OPTIONAL', b'CERT OPTIONAL'),
                             (b'CERT_REQUIRED', b'CERT REQUIRED')])),
                ('ssl_options', models.CharField(
                    help_text=b"(Optional) Comma-separated list of SSL "
                              b"module options. If undefined, defaults to "
                              b"'OP_NO_SSLv2, OP_NO_SSLv3, OP_NO_COMPRESSION'."
                              b" See ssl OP_* constant documentation for "
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
                              b'same, but skips raising an error.',
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
                              b'the same, but skips raising an error.',
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
        migrations.CreateModel(
            name='HostnamePortSslConfig',
            fields=[
                ('hostname_port', models.CharField(
                    primary_key=True, serialize=False, max_length=255,
                    help_text=b"Hostname and (optional) port, e.g. "
                              b"'mydomain.com' or 'mydomain.com:8000'. "
                              b"MUST be all lowercase.",
                    unique=True, verbose_name=b'Hostname:Port')),
                ('ssl_config', models.ForeignKey(
                    related_name='+', verbose_name=b'Ssl config',
                    to='pki.SslConfig', null=True)),
            ],
            options={
                'ordering': ['hostname_port'],
                'verbose_name': 'Hostname:Port to SSL Config Map',
                'verbose_name_plural': 'Hostname:Port to SSL Config Mappings',
            },
        ),
        migrations.AlterUniqueTogether(
            name='hostnameportsslconfig',
            unique_together=set([('hostname_port', 'ssl_config')]),
        ),
    ]
