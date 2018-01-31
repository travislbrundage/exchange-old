# IMPORTANT: this directory should not be within application or www roots
# For dev testing, either create a symlink from this location to:
# <django project source>/pki/tests/files
PKI_DIRECTORY = '/usr/local/exchange-pki'

"""
name:
    string; REQUIRED (display name of config, shown in popup on remote services
    registration page and details page after registration)

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

SSL_CONFIGS = {}

"""
Example for adding new configs beyond the default

SSL_CONFIGS = {
    'config1': {
        "name": "TLS v1.2-only network",
        "ca_custom_certs": "/path/to/ca_certs.crt",
        "ssl_version": ssl.PROTOCOL_TLSv1_2
    },
    'config2': {
        "name": "TLS v1.2-only network with PKI",
        "ca_custom_certs": "/path/to/ca_certs.crt",
        "client_cert": "/path/to/npe_cert.crt",
        "client_key": "/path/to/npe.key",
        "client_key_pass": "password",
        "ssl_version": ssl.PROTOCOL_TLSv1_2
    }
}

Note: It is NOT required to implement all settings in new configs, any values
that are excluded will assume the values of SSL_DEFAULT_CONFIG
"""

# This TEMPORARILY represents an ssl_config_map model
SSL_CONFIG_MAP = {}
