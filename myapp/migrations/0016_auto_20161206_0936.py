# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0015_auto_20161205_1547'),
    ]

    operations = [
        migrations.AlterField(
            model_name='db_account',
            name='tags',
            field=models.CharField(max_length=30, db_index=True),
        ),
    ]
