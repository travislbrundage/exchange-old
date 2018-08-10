# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pki', '0004_proxy_mapping_table'),
    ]

    operations = [
        migrations.CreateModel(
            name='SslLogEntry',
            fields=[
                ('id', models.AutoField(
                    verbose_name='ID',
                    serialize=False,
                    auto_created=True,
                    primary_key=True)
                 ),
                ('timestamp', models.DateTimeField(
                    auto_now_add=True,
                    verbose_name=b'Timestamp')
                 ),
                ('level', models.CharField(
                    max_length=10,
                    verbose_name=b'Level')
                 ),
                ('message', models.TextField(
                    verbose_name=b'Message')
                 ),
            ],
            options={
                'ordering': ['-timestamp'],
                'verbose_name': 'SSL/PKI Log Entry',
                'verbose_name_plural': 'SSL/PKI Log Entries',
            },
        ),
    ]
