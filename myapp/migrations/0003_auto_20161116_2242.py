# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0002_auto_20161116_1422'),
    ]

    operations = [
        migrations.AlterField(
            model_name='db_account',
            name='role',
            field=models.CharField(default='all', max_length=30, choices=[('read', 'read'), ('write', 'write'), ('all', 'all'), ('admin', 'admin')]),
        ),
    ]
