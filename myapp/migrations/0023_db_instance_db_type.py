# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0022_auto_20170122_1620'),
    ]

    operations = [
        migrations.AddField(
            model_name='db_instance',
            name='db_type',
            field=models.CharField(default='mysql', max_length=30),
        ),
    ]
