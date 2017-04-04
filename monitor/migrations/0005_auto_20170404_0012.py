# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('monitor', '0004_auto_20170404_0005'),
    ]

    operations = [
        migrations.AlterField(
            model_name='mysql_processlist',
            name='info',
            field=models.TextField(null=True),
        ),
        migrations.AlterField(
            model_name='mysql_processlist',
            name='state',
            field=models.CharField(max_length=64, null=True),
        ),
    ]
