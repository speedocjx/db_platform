# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('monitor', '0014_auto_20170405_1629'),
    ]

    operations = [
        migrations.CreateModel(
            name='alarm',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('db_ip', models.CharField(max_length=30)),
                ('db_port', models.CharField(max_length=10)),
                ('alarm_type', models.CharField(max_length=30)),
                ('alarmed_times', models.IntegerField()),
                ('create_time', models.DateTimeField(db_index=True)),
            ],
            options={
                'db_table': 'alarm',
            },
        ),
        migrations.RemoveField(
            model_name='mysqlstatus',
            name='threads_waits',
        ),
        migrations.RemoveField(
            model_name='mysqlstatushis',
            name='threads_waits',
        ),
        migrations.AlterIndexTogether(
            name='alarm',
            index_together=set([('db_ip', 'db_port')]),
        ),
    ]
