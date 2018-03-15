# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pki', '0002_default_config'),
    ]

    operations = [
        migrations.AddField(
            model_name='hostnameportsslconfig',
            name='enabled',
            field=models.BooleanField(
                default=True,
                help_text=b'Whether mapping is enabled',
                verbose_name=b'Enabled'
            ),
        ),
        migrations.AddField(
            model_name='hostnameportsslconfig',
            name='order',
            field=models.PositiveIntegerField(
                default=1000,
                editable=False,
                db_index=True
            ),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='hostnameportsslconfig',
            name='hostname_port',
            field=models.CharField(
                primary_key=True,
                serialize=False,
                max_length=255,
                help_text=b"(REQUIRED) Hostname and (optional) port. MUST be "
                          b"all lowercase.<br/><br/>Examples:<br/>"
                          b"<b>mydomain.com</b><br/><b>mydomain.com:8000</b>"
                          b"<br/><br/>Wildcard '*' character matching is "
                          b"supported (use sparingly).<br/><br/>Examples:<br/>"
                          b"<b>*.mydomain.com</b> (matches subdomains)<br/>"
                          b"<b>*.mydomain.com*</b> "
                          b"(matches subdomains and all ports)<br/>"
                          b"<b>*.*</b> (matches ALL https requests; avoid "
                          b"unless necessary)<br/><br/><em>Use admin list "
                          b"view to sort patterns for matching.</em>",
                unique=True,
                verbose_name=b'Hostname:Port'
            ),
        ),
        migrations.AlterModelOptions(
            name='hostnameportsslconfig',
            options={
                'ordering': ('order',),
                'verbose_name': 'Hostname:Port >> SSL Config',
                'verbose_name_plural': 'Hostname:Port >> SSL Configs'
            },
        ),
    ]
