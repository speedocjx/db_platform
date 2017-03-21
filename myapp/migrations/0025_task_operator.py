# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0024_auto_20170214_1508'),
    ]

    operations = [
        migrations.AddField(
            model_name='task',
            name='operator',
            field=models.CharField(default='', max_length=35),
        ),
    ]
