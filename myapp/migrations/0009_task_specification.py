# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0008_auto_20161126_1555'),
    ]

    operations = [
        migrations.AddField(
            model_name='task',
            name='specification',
            field=models.CharField(default='', max_length=50),
        ),
    ]
