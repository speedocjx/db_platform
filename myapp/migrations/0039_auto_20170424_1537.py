# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0038_task_backup_status'),
    ]

    operations = [
        migrations.AlterField(
            model_name='incep_error_log',
            name='sequence',
            field=models.CharField(max_length=30, db_index=True),
        ),
    ]
