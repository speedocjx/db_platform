# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0019_auto_20161217_1832'),
    ]

    operations = [
        migrations.AlterField(
            model_name='db_instance',
            name='role',
            field=models.CharField(max_length=30, choices=[('read', 'read'), ('write', 'write'), ('all', 'all'), ('idle', 'idle')]),
        ),
    ]
