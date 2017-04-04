# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('monitor', '0005_auto_20170404_0012'),
    ]

    operations = [
        migrations.AlterField(
            model_name='mysql_processlist',
            name='create_time',
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
    ]
