# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('monitor', '0016_auto_20170406_1352'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='alarm',
            name='alarmed_times',
        ),
        migrations.AddField(
            model_name='alarm',
            name='send_mail',
            field=models.SmallIntegerField(default=0),
        ),
    ]
