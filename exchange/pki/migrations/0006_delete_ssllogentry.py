# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('pki', '0005_ssllogentry'),
    ]

    operations = [
        migrations.DeleteModel(
            name='SslLogEntry',
        ),
    ]
