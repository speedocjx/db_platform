# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0041_auto_20170512_1516'),
    ]

    operations = [
        migrations.AlterField(
            model_name='tb_blacklist',
            name='dbtag',
            field=models.CharField(unique=True, max_length=255),
        ),
    ]
