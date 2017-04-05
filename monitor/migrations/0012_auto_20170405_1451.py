# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('monitor', '0011_auto_20170405_1432'),
    ]

    operations = [
        migrations.AlterField(
            model_name='mysql_replication',
            name='create_time',
            field=models.DateTimeField(),
        ),
        migrations.AlterField(
            model_name='mysql_replication_his',
            name='create_time',
            field=models.DateTimeField(),
        ),
    ]
