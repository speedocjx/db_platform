# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0009_task_specification'),
    ]

    operations = [
        migrations.AlterField(
            model_name='task',
            name='specification',
            field=models.CharField(default='', max_length=100),
        ),
    ]
