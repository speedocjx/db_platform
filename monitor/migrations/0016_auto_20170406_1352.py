# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('monitor', '0015_auto_20170406_1339'),
    ]

    operations = [
        migrations.AlterField(
            model_name='alarm',
            name='create_time',
            field=models.DateTimeField(default=django.utils.timezone.now, db_index=True),
        ),
    ]
