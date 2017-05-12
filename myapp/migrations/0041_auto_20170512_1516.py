# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0040_tb_blacklist'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='tb_blacklist',
            name='db',
        ),
        migrations.AddField(
            model_name='tb_blacklist',
            name='dbtag',
            field=models.CharField(default='lepus', max_length=255, db_index=True),
            preserve_default=False,
        ),
    ]
