# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Saltrecord',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('conn_id', models.CharField(max_length=30)),
                ('user', models.CharField(max_length=32)),
                ('host', models.CharField(max_length=64)),
                ('db', models.CharField(max_length=64)),
                ('command', models.CharField(max_length=16)),
                ('time', models.IntegerField()),
                ('state', models.CharField(max_length=64)),
                ('info', models.TextField()),
                ('create_time', models.DateTimeField()),
            ],
            options={
                'db_table': 'mysql_processlist',
            },
        ),
    ]
