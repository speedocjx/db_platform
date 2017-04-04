# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('monitor', '0002_auto_20170403_2329'),
    ]

    operations = [
        migrations.RenameField(
            model_name='mysql_processlist',
            old_name='info',
            new_name='sqltext',
        ),
    ]
