# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import datetime
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('salt', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='saltrecord',
            name='return_field',
        ),
        migrations.AddField(
            model_name='saltrecord',
            name='arg',
            field=models.CharField(default=datetime.datetime(2017, 1, 25, 2, 39, 54, 704543, tzinfo=utc), max_length=50),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='saltrecord',
            name='tgt',
            field=models.CharField(default=1, max_length=100),
            preserve_default=False,
        ),
    ]
