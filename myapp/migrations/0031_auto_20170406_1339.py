# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0030_mysql_monitor_replchannel'),
    ]

    operations = [
        migrations.AddField(
            model_name='mysql_monitor',
            name='alarm_interval',
            field=models.SmallIntegerField(default=60),
        ),
        migrations.AddField(
            model_name='mysql_monitor',
            name='alarm_time',
            field=models.SmallIntegerField(default=3),
        ),
    ]
