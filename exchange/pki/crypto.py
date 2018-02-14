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

# for cryptography's Fernet
import base64
from cryptography.fernet import Fernet, InvalidToken
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

from django.conf import settings


class CryptoInvalidToken(InvalidToken):
    pass


class Crypto(object):

    def __init__(self):
        password = settings.SECRET_KEY
        salt = 'T\x96\xb1\x17\x199\xde{\x0cu\x97\x9an\x83\xd3\xa0'
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
            backend=default_backend()
        )
        key = base64.urlsafe_b64encode(kdf.derive(password))
        self._fernet = Fernet(key)

    @staticmethod
    def _proof_input(data):
        """
        Django return unicode from the database.
        Convert it to bytes, as Fernet requires that for input.
        """
        # noinspection PyCompatibility
        if not isinstance(data, (basestring, bytes)):  # noqa
            raise TypeError(
                'Encrypt/decrypt data must be a basestring subclass or bytes')
        if isinstance(data, unicode):  # noqa
            try:
                return data.encode('UTF-8')
            except UnicodeEncodeError:
                raise UnicodeEncodeError(
                    'Encrypt/decrypt unicode data could not encode to UTF-8')
        return data

    def encrypt(self, data):
        return self._fernet.encrypt(self._proof_input(data))

    def decrypt(self, data):
        try:
            out = self._fernet.decrypt(self._proof_input(data))
        except InvalidToken:
            raise CryptoInvalidToken

        return out
