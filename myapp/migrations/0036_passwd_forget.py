# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0035_auto_20170410_1335'),
    ]

    operations = [
        migrations.CreateModel(
            name='Passwd_forget',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('username', models.CharField(max_length=30)),
                ('vc_value', models.CharField(max_length=40, db_index=True)),
                ('create_time', models.DateTimeField()),
            ],
        ),
    ]
