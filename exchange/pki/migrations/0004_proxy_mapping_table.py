# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pki', '0003_update_mapping_table'),
    ]

    operations = [
        migrations.AddField(
            model_name='hostnameportsslconfig',
            name='proxy',
            field=models.BooleanField(
                default=True,
                help_text=b"Whether to require client's browser connections "
                          b"to be proxied through this application.",
                verbose_name=b'Proxy'),
        ),
    ]
