# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('passforget', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='passwd_forget',
            name='is_valid',
            field=models.SmallIntegerField(default=1),
        ),
        migrations.AlterIndexTogether(
            name='passwd_forget',
            index_together=set([('username', 'is_valid')]),
        ),
    ]
