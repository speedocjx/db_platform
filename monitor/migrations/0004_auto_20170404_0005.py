# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('monitor', '0003_auto_20170404_0000'),
    ]

    operations = [
        migrations.RenameField(
            model_name='mysql_processlist',
            old_name='sqltext',
            new_name='info',
        ),
    ]
