# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0027_mysql_monitor'),
    ]

    operations = [
        migrations.AddField(
            model_name='mysql_monitor',
            name='monitor',
            field=models.SmallIntegerField(default=1),
        ),
    ]
