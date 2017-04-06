# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0029_mysql_monitor_longsql_autokill'),
    ]

    operations = [
        migrations.AddField(
            model_name='mysql_monitor',
            name='replchannel',
            field=models.CharField(default='0', max_length=30),
        ),
    ]
