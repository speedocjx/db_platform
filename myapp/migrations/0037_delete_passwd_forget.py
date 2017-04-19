# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0036_passwd_forget'),
    ]

    operations = [
        migrations.DeleteModel(
            name='Passwd_forget',
        ),
    ]
