# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0006_login_log'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='login_log',
            name='login_time',
        ),
    ]
