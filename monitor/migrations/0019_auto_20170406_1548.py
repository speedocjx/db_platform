# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('monitor', '0018_auto_20170406_1510'),
    ]

    operations = [
        migrations.AlterIndexTogether(
            name='alarmtemp',
            index_together=set([('db_ip', 'db_port', 'alarm_type')]),
        ),
    ]
