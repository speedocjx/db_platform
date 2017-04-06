# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0031_auto_20170406_1339'),
    ]

    operations = [
        migrations.AlterField(
            model_name='mysql_monitor',
            name='instance',
            field=models.ForeignKey(to='myapp.Db_instance'),
        ),
    ]
