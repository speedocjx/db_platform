# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('monitor', '0017_auto_20170406_1405'),
    ]

    operations = [
        migrations.CreateModel(
            name='AlarmTemp',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('db_ip', models.CharField(max_length=30)),
                ('db_port', models.CharField(max_length=10)),
                ('alarm_type', models.CharField(max_length=30)),
                ('send_mail', models.SmallIntegerField(default=0)),
                ('create_time', models.DateTimeField(default=django.utils.timezone.now, db_index=True)),
            ],
            options={
                'db_table': 'alarm_temp',
            },
        ),
        migrations.AlterIndexTogether(
            name='alarmtemp',
            index_together=set([('db_ip', 'db_port')]),
        ),
    ]
