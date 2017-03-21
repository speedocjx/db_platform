# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0013_auto_20161201_1726'),
    ]

    operations = [
        migrations.AlterField(
            model_name='db_group',
            name='groupname',
            field=models.CharField(unique=True, max_length=30),
        ),
    ]
