# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0020_auto_20161219_1550'),
    ]

    operations = [
        migrations.AddField(
            model_name='user_profile',
            name='task_email',
            field=models.IntegerField(default=0, db_index=True),
            preserve_default=False,
        ),
    ]
