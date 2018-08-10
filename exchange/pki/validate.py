# -*- coding: utf-8 -*-
#########################################################################
#
# Copyright (C) 2018 Boundless Spatial
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

import datetime
import hashlib
import logging

# noinspection PyCompatibility
from exceptions import UserWarning

from cryptography import x509
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.asymmetric import padding, utils
from cryptography.exceptions import InvalidSignature

from six import text_type, binary_type, PY3

from .settings import get_pki_dir
from .utils import pki_file, file_readable
from .pem import parse, Certificate

logger = logging.getLogger(__name__)

ACCEPTABLE_FORMATS = 'PEM'  # not parsed, just display text


class PkiValidationError(Exception):
    def __init__(self, msgs):
        self.msgs = msgs
        super(PkiValidationError, self).__init__(self.__str__())

    def __str__(self):
        if isinstance(self.msgs, list):
            encoded_list = [m.encode('utf-8') for m in self.msgs]
            return b' \n\n'.join(encoded_list)
        else:
            return self.msgs.encode('utf-8')

    def message_list(self):
        if isinstance(self.msgs, list):
            return self.msgs
        else:
            return [self.msgs]

    def message_html(self):
        return u'<br>'.join(self.message_list())


class PkiValidationWarning(UserWarning):
    def __init__(self, msgs):
        self.msgs = msgs
        super(PkiValidationWarning, self).__init__(self.__str__())

    def __str__(self):
        if isinstance(self.msgs, list):
            encoded_list = [m.encode('utf-8') for m in self.msgs]
            return b' \n\n'.join(encoded_list)
        else:
            return self.msgs.encode('utf-8')

    def message_list(self):
        if isinstance(self.msgs, list):
            return self.msgs
        else:
            return [self.msgs]

    def message_html_pre(self):
        return u"<pre>\n{0}\n</pre>".format(u' \n\n'.join(self.msgs))


# From OpenSSL._util protected member
def native(s):
    """
    Convert :py:class:`bytes` or :py:class:`unicode` to the native
    :py:class:`str` type, using UTF-8 encoding if conversion is necessary.

    :raise UnicodeError: The input string is not UTF-8 decodeable.

    :raise TypeError: The input is neither :py:class:`bytes` nor
        :py:class:`unicode`.
    """
    if s is None:
        return None
    if not isinstance(s, (binary_type, text_type)):
        raise TypeError("%r is neither bytes nor unicode" % s)
    if PY3:
        if isinstance(s, binary_type):
            return s.decode("utf-8")
    else:
        if isinstance(s, text_type):
            return s.encode("utf-8")
    return s


def pki_dir_path(file_name):
    """
        Ensure file path is prepended with PKI_DIRECTORY.

        :param file_name: Name or path of file in PKI_DIRECTORY
        :rtype: str
        """
    return file_name if file_name.startswith(get_pki_dir()) \
        else pki_file(file_name.lstrip('/'))


def pki_file_exists_readable(file_name):
    """
    Validate file name exists in PKI_DIRECTORY and is readable.

    :param file_name: Name or path of file in PKI_DIRECTORY
    :rtype: bool
    """
    return file_readable(pki_dir_path(file_name))


def pki_file_contents(file_name):
    """
    Return PKI file contents as bytes.

    :param file_name: Name or path of file in PKI_DIRECTORY
    :rtype: bytes
    """
    f = pki_dir_path(file_name)
    content = b''
    if not pki_file_exists_readable(f):
        return content

    content = open(f).read()
    if isinstance(content, text_type):
        # TODO: Assumes conversion to PEM from unicode (not robust enough)
        # Though, it is the same thing pyOpenSSL does
        content = content.encode('ASCII')
    return content


def pki_acceptable_format(file_data):
    """
    Whether a PKI component's format is in ACCEPTABLE_FORMATS

    :param file_data: File contents to test
    :return: Whether format is acceptable
    :rtype: bool
    """
    # Test for PEM headers
    pem_headers = [
        'BEGIN CERTIFICATE',
        'BEGIN X509 CERTIFICATE',
        'BEGIN RSA PRIVATE KEY',
        'BEGIN PRIVATE KEY',
        'BEGIN ENCRYPTED PRIVATE KEY',
    ]
    for h in pem_headers:
        if h in file_data:
            return True

    # TODO: Consider supporting DER, i.e. ASN1? Or, possibly PKCS#12?

    return False


def cert_date_not_yet_valid(cert_data):
    """
    Whether a certificate's start date is currently invalid, e.g. before
    'not before' date.

    :param cert_data: Cert data to test
    :type cert_data: bytes | x509.Certificate
    :rtype: bool
    """
    if not cert_data:
        return True

    if isinstance(cert_data, x509.Certificate):
        cert = cert_data
    else:
        try:
            cert = x509.load_pem_x509_certificate(cert_data, default_backend())
            """:type: x509.Certificate"""
        except ValueError:
            return True

    return datetime.datetime.utcnow() < cert.not_valid_before


def cert_date_expired(cert_data):
    """
    Whether a certificate's end date has passed, e.g. after 'not after' date.

    :param cert_data: Cert data to test
    :type cert_data: bytes | x509.Certificate
    :rtype: bool
    """
    if not cert_data:
        return True

    if isinstance(cert_data, x509.Certificate):
        cert = cert_data
    else:
        try:
            cert = x509.load_pem_x509_certificate(cert_data, default_backend())
            """:type: x509.Certificate"""
        except ValueError:
            return True

    return cert.not_valid_after < datetime.datetime.utcnow()


def is_ca_cert(cert_data, require_key_usage=True):
    """
    Whether a certificate is a Certificate Authority

    :param cert_data: Cert data to test
    :type cert_data: bytes | x509.Certificate
    :param require_key_usage: Whether to also require cert signing in KeyUsage
    extension as well
    :rtype: bool
    """
    if not cert_data:
        return False

    if isinstance(cert_data, x509.Certificate):
        cert = cert_data
    else:
        try:
            cert = x509.load_pem_x509_certificate(cert_data, default_backend())
            """:type: x509.Certificate"""
        except ValueError:
            return False

    try:
        constraints_ext = cert.extensions.get_extension_for_class(
            x509.BasicConstraints
        )
        """:type: x509.Extension"""
    except x509.ExtensionNotFound:
        return False

    basic_constraints = constraints_ext.value
    """:type: x509.BasicConstraints"""
    res = basic_constraints.ca

    if res and require_key_usage:
        try:
            key_usage_ext = cert.extensions.get_extension_for_class(
                x509.KeyUsage
            )
            """:type: x509.Extension"""
        except x509.ExtensionNotFound:
            return False

        key_usage = key_usage_ext.value
        """:type: x509.KeyUsage"""
        res = key_usage.key_cert_sign

    return res


def is_client_cert(cert_data, require_extended_key_usage=False):
    """
    Validate public cert is capable of being used as client cert

    :param cert_data: Cert data to test
    :type cert_data: bytes | x509.Certificate
    :param require_extended_key_usage: Whether to also require client cert in
    extended key usage extension as well
    :rtype: bool
    """
    if not cert_data:
        return False

    if is_ca_cert(cert_data):
        return False

    if isinstance(cert_data, x509.Certificate):
        cert = cert_data
    else:
        try:
            cert = x509.load_pem_x509_certificate(cert_data, default_backend())
            """:type: x509.Certificate"""
        except ValueError:
            return False

    try:
        key_usage_ext = cert.extensions.get_extension_for_class(
            x509.KeyUsage
        )
        """:type: x509.Extension"""
    except x509.ExtensionNotFound:
        return False

    key_usage = key_usage_ext.value
    """:type: x509.KeyUsage"""
    res = (key_usage.digital_signature and
           key_usage.key_encipherment)

    if res and require_extended_key_usage:
        try:
            extended_key_usage = cert.extensions.get_extension_for_oid(
                x509.ExtensionOID.EXTENDED_KEY_USAGE
            )
            """:type: x509.Extension"""
        except x509.ExtensionNotFound:
            return False
        return x509.ExtendedKeyUsageOID.CLIENT_AUTH in extended_key_usage.value

    return res


def cert_subject_common_name(cert_data):
    """
    Return certificate's common name under subject info.

    :param cert_data: Certificate data already parsed
    :type cert_data: x509.Certificate
    :rtype: unicode
    """
    if isinstance(cert_data, x509.Certificate):
        cmn_names = cert_data.subject.get_attributes_for_oid(
            x509.oid.NameOID.COMMON_NAME)
        if cmn_names:
            cmn_name = cmn_names[0].value
            return cmn_name if cmn_name \
                else u'(Certificate lacks common name)'

    return u'(No common name found)'


def load_certs(cert_data):
    """
    Return list of any certs contained in data. Does no validation beyond
    whether the cert can be loaded into an x509. Certificate object. Does not
    check for valid format of data, e.g. PEM, etc.

    :param cert_data: Certificate data to parse and load
    :type cert_data: bytes
    :rtype: Tuple[list, list,]
    """
    certs = []
    msg = []

    parsed_pem = parse(cert_data)
    certs_pem = [c.as_bytes() for c in parsed_pem
                 if isinstance(c, Certificate)]
    # logging.debug('certs_pem: {0}'.format(certs_pem))

    for cert_pem in certs_pem:
        try:
            cert = x509.load_pem_x509_certificate(cert_pem, default_backend())
            certs.append(cert)
        except Exception as e:
            # log un-loadable certs
            cert_parts = cert_pem.splitlines()
            cert_line = cert_parts[1] if len(cert_parts) > 1 else ''
            msg.append('{0}: (first line) {1}'.format(e.message, cert_line))

    return certs, msg


def load_first_cert(cert_data):
    """
    Parse cert data and return first found certificate. Does not return any
    warnings logged during parsing.

    :param cert_data: Certificate data to parse and load
    :type cert_data: bytes
    :rtype: None | x509.Certificate
    """
    certs, _ = load_certs(cert_data)

    return certs[0] if certs else None


def load_private_key(key_data, password=None):
    """
    Validate private key can be loaded, decrypting with any supplied password

    :param key_data: Private key data to parse and load
    :type key_data: bytes
    :param password: Optional password of private key
    :return: x509 private key or raises PkiValidationError
    :rtype: rsa.RSAPrivateKey | dsa.DSAPrivateKey | ec.EllipticCurvePrivateKey
    """
    msg = []
    priv_key = None
    try:
        priv_key = serialization.load_pem_private_key(
            key_data,
            None if not password else native(password),
            default_backend()
        )
    except ValueError as e:
        msg.append('ValueError: {0}'.format(e.message))
    except TypeError as e:
        msg.append('TypeError: {0}'.format(e.message))

    if msg:
        raise PkiValidationError(msg)

    return priv_key


def validate_cert_matches_private_key(cert_data, key_data, password=None):
    """
    Validate a cert and private key match, and signature can be verified

    :param cert_data: Cert data to test
    :type cert_data: bytes
    :param key_data: Private key data to test
    :type key_data: bytes
    :param password: Optional password of private key
    :return: List of any warnings or raises PkiValidationError
    :rtype: list
    """
    warn = []

    priv_key = load_private_key(key_data, password=password)
    priv_pub_key = priv_key.public_key()

    certs, msgs = load_certs(cert_data)
    if not certs:
        raise PkiValidationError(
            'No certificate found to match against private key.')
    if len(certs) > 1:
        warn.append('Multiple certificates found to compare against key. '
                    'Using first.')
    if msgs:
        warn.extend(msgs)
    cert = certs[0]
    """:type: x509.Certificate"""
    cert_pub_key = cert.public_key()

    priv_pub_key_pem = priv_pub_key.public_bytes(
        serialization.Encoding.PEM,
        serialization.PublicFormat.SubjectPublicKeyInfo
    )
    cert_pub_key_pem = cert_pub_key.public_bytes(
        serialization.Encoding.PEM,
        serialization.PublicFormat.SubjectPublicKeyInfo
    )
    if priv_pub_key_pem != cert_pub_key_pem:
        raise PkiValidationError(
            'Public keys of certificate and private key do not match.')

    # See cryptography.hazmat.primitives.asymmetric.utils.Prehashed example
    prehashed_msg = hashlib.sha256(b"A message I want to sign").digest()
    signature = priv_key.sign(
        prehashed_msg,
        padding.PSS(
            mgf=padding.MGF1(hashes.SHA256()),
            salt_length=padding.PSS.MAX_LENGTH
        ),
        utils.Prehashed(hashes.SHA256())
    )
    try:
        priv_pub_key.verify(
            signature,
            prehashed_msg,
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH
            ),
            utils.Prehashed(hashes.SHA256())
        )
    except InvalidSignature:
        raise PkiValidationError(
            'Private key signature could not be verified with certificate '
            'public key.')

    return warn


def validate_cert_file_matches_key_file(cert_file_name, key_file_name,
                                        password=None):
    """
    Validate a cert and private key match, and signature can be verified

    :param cert_file_name: Name or path of file in PKI_DIRECTORY
    :param key_file_name: Name or path of file in PKI_DIRECTORY
    :param password: Optional password of private key
    :return: List of any warnings or raises PkiValidationError
    :rtype: list
    """
    return validate_cert_matches_private_key(
        pki_file_contents(cert_file_name),
        pki_file_contents(key_file_name),
        password=password
    )


def validate_ca_certs(file_name, allow_expired=True):
    """
    Validate all CAs in file (skip expired, if 'allow expired' set).

    :param file_name: Name or path of file in PKI_DIRECTORY containing one or
    more CA certs
    :param allow_expired: Whether to allow expired CAs, but otherwise valid
    :return: List of any warnings or raises PkiValidationError
    :rtype: list
    """
    warn = []

    if not pki_file_exists_readable(file_name):
        raise PkiValidationError(
            'Defined CA certs file can not be located or read.')

    if not pki_acceptable_format(pki_file_contents(file_name)):
        raise PkiValidationError(
            "Defined CA certs file not in acceptable format (use {0})"
            .format(ACCEPTABLE_FORMATS))

    certs, warns = load_certs(pki_file_contents(file_name))
    if not certs:
        raise PkiValidationError(
            'Defined CA certs file has no readable certificates.')
    if warns:
        warn.extend(warns)

    ca_certs = [c for c in certs if is_ca_cert(c, require_key_usage=True)]
    if not ca_certs:
        raise PkiValidationError(
            'Defined CA certs file has no readable Certificate Authorities.')

    expired_certs = [cert_subject_common_name(c) for c in ca_certs
                     if cert_date_expired(c)]
    if expired_certs:
        cn_msg = (u"Defined CA certs file contains CAs that are expired "
                  u"(common names): \n{0}"
                  .format(", \n".join(expired_certs)))
        if allow_expired:
            warn.append(cn_msg)
        else:
            raise PkiValidationError(cn_msg)

    return warn


def validate_client_cert(cert_file_name):
    """
    Validate a client certificate file.

    :param cert_file_name: Name or path of file in PKI_DIRECTORY
    :return: List of any warnings or raises PkiValidationError
    :rtype: list
    """
    warn = []

    if not pki_file_exists_readable(cert_file_name):
        raise PkiValidationError(
            'Defined client cert file can not be located or read.')

    if not pki_acceptable_format(pki_file_contents(cert_file_name)):
        raise PkiValidationError(
            "Defined client cert file not in acceptable format (use {0})"
            .format(ACCEPTABLE_FORMATS))

    certs, warns = load_certs(pki_file_contents(cert_file_name))
    if not certs:
        raise PkiValidationError(
            'Defined client cert file has no readable certificates.')
    if warns:
        warn.extend(warns)

    c_certs = [c for c in certs
               if is_client_cert(c, require_extended_key_usage=False)]
    if not c_certs:
        raise PkiValidationError(
            'Defined client cert file has no readable client certs.')

    if len(c_certs) > 1:
        warn.append('Defined client cert file has multiple client certs. '
                    'First will be used.')

    client_cert = c_certs[0]

    # Makes sense to warn about 'not yet valid' certs, but not to block any
    # form submission with a validation error.
    if cert_date_not_yet_valid(client_cert):
        warn.append('Defined client cert file is not yet valid')

    if cert_date_expired(client_cert):
        raise PkiValidationError('Defined client cert file is expired')

    return warn


def validate_client_key(key_file_name, password=None):
    """
    Validate a client private key file.

    :param key_file_name: Name or path of file in PKI_DIRECTORY
    :param password: Optional password of private key
    :return: List of any warnings or raises PkiValidationError
    :rtype: list
    """
    warn = []
    # TODO: No warnings logged yet

    if not pki_file_exists_readable(key_file_name):
        raise PkiValidationError(
            'Defined client key file can not be located or read.')

    if not pki_acceptable_format(pki_file_contents(key_file_name)):
        raise PkiValidationError(
            "Defined client key file not in acceptable format (use {0})"
            .format(ACCEPTABLE_FORMATS))

    key = load_private_key(pki_file_contents(key_file_name),
                           password=password)

    if not hasattr(key, 'private_bytes'):
        raise PkiValidationError(
            'Defined client key file could not be loaded.')

    return warn
