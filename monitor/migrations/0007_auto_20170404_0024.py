# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('monitor', '0006_auto_20170404_0016'),
    ]

    operations = [
        migrations.AddField(
            model_name='mysql_processlist',
            name='db_ip',
            field=models.CharField(default='127.0.0.1', max_length=20),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='mysql_processlist',
            name='db_port',
            field=models.SmallIntegerField(default=3306),
            preserve_default=False,
        ),
    ]
