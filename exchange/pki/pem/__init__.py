from __future__ import absolute_import, division, print_function

from ._core import (
    Certificate,
    CertificateRequest,
    DHParameters,
    Key,
    RSAPrivateKey,
    parse,
    parse_file,
)


__version__ = "17.1.0"
__author__ = "Hynek Schlawack"
__license__ = "MIT"
__description__ = "Easy PEM file parsing in Python."
__uri__ = "https://pem.readthedocs.io/"
__email__ = "hs@ox.cx"


_DEPRECATION_WARNING = (
    "Calling {func} from the pem package is deprecated as of pem 15.0.0.  "
    "Please use pem.twisted.{func} instead."
)


__all__ = [
    "Certificate",
    "CertificateRequest",
    "DHParameters",
    "Key",
    "RSAPrivateKey",
    "parse",
    "parse_file",
]
