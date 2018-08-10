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

from __future__ import unicode_literals

from django.db import migrations

from ..settings import SSL_DEFAULT_CONFIG


def load_default_config(apps, schema_editor):
    sslconfig = apps.get_model('pki', 'SslConfig')
    db_alias = schema_editor.connection.alias
    ssl_config = sslconfig(**SSL_DEFAULT_CONFIG)
    ssl_config.save(using=db_alias)


def delete_default_config(apps, schema_editor):
    sslconfig = apps.get_model('pki', 'SslConfig')
    db_alias = schema_editor.connection.alias
    sslconfig.objects.using(db_alias).get(pk=1).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('pki', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(load_default_config, delete_default_config),
    ]
