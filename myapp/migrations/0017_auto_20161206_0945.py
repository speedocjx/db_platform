# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0016_auto_20161206_0936'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='db_instance',
            unique_together=set([('ip', 'port')]),
        ),
    ]
