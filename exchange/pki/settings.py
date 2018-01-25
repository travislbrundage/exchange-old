import os
import ssl

'''
name:                       string (display name of config, shown in popup on
                            remote services registration page and details page
                            after registration)

ca_custom_certs:            filesystem path; default None

ca_use_system:              bool; default True (if True, any custom certs are
                            appended)

ca_allow_invalid_certs:     bool; default False

ca_skip_peer_validation:    bool; default False

client_cert:                filesystem path; default None

client_key:                 filesystem path; default None

client_key_pass:            string; default None

ssl_allow_insecure:         bool; default False

ssl_version:                string; default {{ssl.PROTOCOL_SSLv23}} (from
                            standard Python {{ssl}} package)
'''
SSL_DEFAULT_CONFIG = {
    "name": "Default",
    "ca_custom_certs": None,
    "ca_use_system": True,
    "ca_allow_invalid_certs": False,
    "ca_skip_peer_validation": False,
    "client_cert": None,
    "client_key": None,
    "client_key_pass": None,
    "ssl_allow_insecure": False,
    "ssl_version": ssl.PROTOCOL_SSLv23
}

SSL_CONFIGS = [SSL_DEFAULT_CONFIG]

'''
Example for adding new configs beyond the default

SSL_CONFIGS = [
    {
        "name": "Some high-security network",
        "ca_custom_certs": "/path/to/ca_certs.crt",
        "ssl_version": ssl.PROTOCOL_TLSv1_2
    },
    {
        "name": "Some high-security network with PKI",
        "ca_custom_certs": "/path/to/ca_certs.crt",
        "client_cert": "/path/to/npe_cert.crt",
        "client_key": "/path/to/npe.key",
        "client_key_pass": "password",
        "ssl_version": ssl.PROTOCOL_TLSv1_2
    }
]

Note: It is NOT required to implement all settings in new configs, any values
that are excluded will assume the values of SSL_DEFAULT_CONFIG

Note: If you add additional configs, you should not include SSL_DEFAULT_CONFIG
in your SSL_CONFIGS list.
'''
