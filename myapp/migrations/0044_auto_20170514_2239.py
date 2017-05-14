# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0043_auto_20170513_0038'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='tb_blacklist',
            name='user_permit',
        ),
        migrations.DeleteModel(
            name='Tb_blacklist',
        ),
    ]
