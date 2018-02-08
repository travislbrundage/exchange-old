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


# IMPORTANT: this directory should not be within application or www roots
def get_pki_dir():
    return os.getenv(
        'PKI_DIRECTORY',
        '/usr/local/exchange-pki'
    )


"""
name:
    string; REQUIRED. Display name of configuration.

ca_custom_certs:
    None or filesystem path; default None.
    If None, urllib3 defaults to None, and OpenSSL system CA certs are used.

ca_allow_invalid_certs:
    bool; default False. Used during validation of SSL components in a config.

client_cert:
    None oir filesystem path; default None.
    Path should be to a PEM file of client cert (with no private key included).
    If None, urllib3 defaults to None.

client_key:
    None or filesystem path (REQUIRED, if client_cert defined); default None.
    Path should be to a PEM file of client cert key
    If None, urllib3 defaults to None.

client_key_pass:
    None or string; default None.
    If None, urllib3 defaults to None.

ssl_version:
    None or string; default 'PROTOCOL_SSLv23'.
    ('PROTOCOL_*' options from standard Python {{ssl}} package).
    If None, urllib3 defaults to PROTOCOL_SSLv23.

ssl_verify_mode:
    None or string; default 'CERT_REQUIRED'.
    ('CERT_*' options from standard Python {{ssl}} package).
    If None, urllib3 defaults to CERT_NONE (insecure).

ssl_options:
    None or list of strings; default None
    ('OP_*' options from standard Python {{ssl}} package.)
    If None, urllib3 defaults to a secure set of options for modern TLS:
    ['OP_NO_SSLv2', 'OP_NO_SSLv3', 'OP_NO_COMPRESSION']
    It is recommend to use these options, plus any you wish to add.

ssl_ciphers:
    None or string of OpenSSL ciphers.
    See: https://wiki.openssl.org/index.php/Manual:Ciphers(1)
         and (https://www.openssl.org/docs/man1.0.2/apps/ciphers.html
              or https://www.openssl.org/docs/man1.1.0/apps/ciphers.html).
    If None, urllib3 defaults to its DEFAULT_CIPHERS.

https_retries:
    None, int >= 0 or False.
    (0 does not retry; False does the same, but skips rasising error.)

https_redirects:
    None or int >= 0 or False.
    (0 doesn't follow redirect; False does the same, but skips rasising error.)
"""
SSL_DEFAULT_CONFIG = {
    "name": "Default",
    "ca_custom_certs": None,
    "ca_allow_invalid_certs": False,
    "client_cert": None,
    "client_key": None,
    "client_key_pass": None,
    "ssl_version": "PROTOCOL_SSLv23",
    "ssl_verify_mode": "CERT_REQUIRED",
    # "ssl_verify_flags": None,  # default flags are good enough
    "ssl_options": None,
    "ssl_ciphers": None,
    "https_retries": 3,
    "https_redirects": 3,
}
