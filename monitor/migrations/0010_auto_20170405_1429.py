# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('monitor', '0009_auto_20170405_1357'),
    ]

    operations = [
        migrations.AddField(
            model_name='mysql_replication',
            name='master_binlog_space',
            field=models.BigIntegerField(default=0),
        ),
        migrations.AddField(
            model_name='mysql_replication_his',
            name='master_binlog_space',
            field=models.BigIntegerField(default=0),
        ),
    ]
