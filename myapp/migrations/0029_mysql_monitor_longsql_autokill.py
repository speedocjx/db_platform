# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0028_mysql_monitor_monitor'),
    ]

    operations = [
        migrations.AddField(
            model_name='mysql_monitor',
            name='longsql_autokill',
            field=models.SmallIntegerField(default=0),
        ),
    ]
