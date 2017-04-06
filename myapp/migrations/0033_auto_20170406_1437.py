# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0032_auto_20170406_1340'),
    ]

    operations = [
        migrations.AddField(
            model_name='mysql_monitor',
            name='check_connections',
            field=models.SmallIntegerField(default=0),
        ),
        migrations.AddField(
            model_name='mysql_monitor',
            name='check_delay',
            field=models.SmallIntegerField(default=0),
        ),
        migrations.AddField(
            model_name='mysql_monitor',
            name='check_slave',
            field=models.SmallIntegerField(default=0),
        ),
        migrations.AddField(
            model_name='mysql_monitor',
            name='connection_threshold',
            field=models.IntegerField(default=1000),
        ),
        migrations.AddField(
            model_name='mysql_monitor',
            name='delay_threshold',
            field=models.IntegerField(default=3600),
        ),
    ]
