# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('maps', '0025_auto_20170801_1228'),
    ]

    operations = [
        migrations.AlterField(
            model_name='map',
            name='supplemental_information_en',
            field=models.TextField(default=b'', max_length=2000, blank=True, help_text='any other descriptive information about the dataset', null=True, verbose_name='supplemental information'),
        ),
    ]
