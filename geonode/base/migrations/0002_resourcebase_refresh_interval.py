# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0001_auto_20180312_1512'),
    ]

    operations = [
        migrations.AddField(
            model_name='resourcebase',
            name='refresh_interval',
            field=models.IntegerField(default=60000, null=True, blank=True),
        ),
    ]
