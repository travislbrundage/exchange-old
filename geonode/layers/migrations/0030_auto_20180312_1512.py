# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('layers', '0029_layer_service'),
    ]

    operations = [
        migrations.AlterField(
            model_name='layer',
            name='supplemental_information_en',
            field=models.TextField(default=b'', max_length=2000, blank=True, help_text='any other descriptive information about the dataset', null=True, verbose_name='supplemental information'),
        ),
    ]
