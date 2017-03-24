# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0025_task_operator'),
    ]

    operations = [
        migrations.AlterField(
            model_name='db_account',
            name='passwd',
            field=models.CharField(max_length=255),
        ),
    ]
