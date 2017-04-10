# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0034_auto_20170406_1548'),
    ]

    operations = [
        migrations.AlterField(
            model_name='mysql_monitor',
            name='account',
            field=models.ForeignKey(to='myapp.Db_account'),
        ),
        migrations.AlterField(
            model_name='mysql_monitor',
            name='instance',
            field=models.OneToOneField(to='myapp.Db_instance'),
        ),
    ]
