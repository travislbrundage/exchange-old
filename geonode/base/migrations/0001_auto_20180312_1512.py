# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('base', 'esri_types_supported'),
    ]

    operations = [
        migrations.AlterField(
            model_name='resourcebase',
            name='supplemental_information',
            field=models.TextField(default=b'', help_text='any other descriptive information about the dataset', max_length=2000, verbose_name='supplemental information', blank=True),
        ),
    ]
