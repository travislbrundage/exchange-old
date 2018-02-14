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

# Portions of code within EncryptedFieldMixin class culled from
# https://github.com/defrex/django-encrypted-fields
# Specifically, from EncryptedFieldMixin in encrypted_fields/fields.py
# That code is licensed under MIT License, as follows (as of 2018-02-04)
#########################################################################
#
# The MIT License (MIT)
#
# Copyright (c) 2013 Aron Jones
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#
#########################################################################

from __future__ import unicode_literals

import os
import types
import logging

from django.conf import settings
from django.db import models
from django import forms

from .settings import get_pki_dir
from .utils import file_readable, pki_file
from .crypto import Crypto, CryptoInvalidToken

logger = logging.getLogger(__name__)


class EncryptedFieldMixin(object):

    def __init__(self, *args, **kwargs):
        # Load crypter to handle encryption/decryption
        self._crypter = Crypto()

        # Prefix encrypted data with a static string to allow filtering
        # of encrypted data vs. non-encrypted data using vanilla queries.
        self.prefix = '___'

        # Ensure the encrypted data does not exceed the max_length
        # of the database. Data truncation is a possibility otherwise.
        self.enforce_max_length = getattr(
            settings,
            'ENFORCE_MAX_LENGTH',
            False
        )

        # noinspection PyArgumentList
        super(EncryptedFieldMixin, self).__init__(*args, **kwargs)

    def to_python(self, value):
        if value is None or not isinstance(value, types.StringTypes):
            return value

        if self.prefix and value.startswith(self.prefix):
            value = value[len(self.prefix):]

            # print('value={0}'.format(value))
            try:
                value = self._crypter.decrypt(value)
            except CryptoInvalidToken:
                pass
            except TypeError:
                pass

        return super(EncryptedFieldMixin, self).to_python(value)

    def get_prep_value(self, value):
        value = super(EncryptedFieldMixin, self).get_prep_value(value)

        if value is None or value == '':
            return value

        return self.prefix + self._crypter.encrypt(value)

    # noinspection PyUnusedLocal
    def get_db_prep_value(self, value, connection, prepared=False):
        if not prepared:
            value = self.get_prep_value(value)

            if self.enforce_max_length:
                if (
                        value and hasattr(self, 'max_length') and
                        self.max_length and
                        len(value) > self.max_length
                ):
                    raise ValueError(
                        'Field {0} max_length={1} encrypted_len={2}'.format(
                            self.name,
                            self.max_length,
                            len(value),
                        )
                    )
        return value

    # noinspection PyUnusedLocal
    def from_db_value(self, value, expression, connection, context):
        return self.to_python(value)


class EncryptedCharField(EncryptedFieldMixin, models.CharField):
    pass


# partially culled from https://stackoverflow.com/questions/7439336
class DynamicFilePathField(models.FilePathField):

    def __init__(self, *args, **kwargs):
        super(DynamicFilePathField, self).__init__(*args, **kwargs)
        if callable(self.path):
            self.pathfunc, self.path = self.path, self.path()

    def get_prep_value(self, value):
        value = super(DynamicFilePathField, self).get_prep_value(value)

        # Only keep the relative path to base dir
        if value and value.strip().startswith(get_pki_dir()):
            value = os.path.relpath(value, get_pki_dir().rstrip(os.sep))

        return value

    # noinspection PyUnusedLocal
    def from_db_value(self, value, expression, connection, context):
        a_file = self.to_python(value)
        if a_file:
            pki_path = pki_file(a_file)
            if file_readable(pki_path):
                return pki_path
        return a_file

    def deconstruct(self):
        name, path, args, kwargs = \
            super(DynamicFilePathField, self).deconstruct()
        if hasattr(self, "pathfunc"):
            kwargs['path'] = self.pathfunc
        return name, path, args, kwargs

    def formfield(self, **kwargs):
        defaults = {
            'path': self.path,
            'match': self.match,
            'recursive': self.recursive,
            'form_class': forms.FilePathField,
            'allow_files': self.allow_files,
            'allow_folders': self.allow_folders,
        }
        defaults.update(kwargs)
        return super(DynamicFilePathField, self).formfield(**defaults)
