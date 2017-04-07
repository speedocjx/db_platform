# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('monitor', '0019_auto_20170406_1548'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='alarmtemp',
            name='send_mail',
        ),
    ]
