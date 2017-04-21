# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0037_delete_passwd_forget'),
    ]

    operations = [
        migrations.AddField(
            model_name='task',
            name='backup_status',
            field=models.SmallIntegerField(default=1),
        ),
    ]
