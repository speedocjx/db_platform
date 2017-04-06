# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0033_auto_20170406_1437'),
    ]

    operations = [
        migrations.RenameField(
            model_name='mysql_monitor',
            old_name='alarm_time',
            new_name='alarm_times',
        ),
    ]
