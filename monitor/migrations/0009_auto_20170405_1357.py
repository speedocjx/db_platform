# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('monitor', '0008_mysql_replication'),
    ]

    operations = [
        migrations.CreateModel(
            name='Mysql_replication_his',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('db_ip', models.CharField(max_length=20)),
                ('db_port', models.SmallIntegerField()),
                ('is_master', models.SmallIntegerField(default=0)),
                ('is_slave', models.SmallIntegerField(default=0)),
                ('read_only', models.CharField(max_length=10)),
                ('gtid_mode', models.CharField(max_length=10)),
                ('master_server', models.CharField(max_length=30)),
                ('master_port', models.CharField(max_length=20)),
                ('slave_io_run', models.CharField(max_length=20)),
                ('slave_sql_run', models.CharField(max_length=20)),
                ('delay', models.CharField(max_length=20)),
                ('current_binlog_file', models.CharField(max_length=30)),
                ('current_binlog_pos', models.CharField(max_length=30)),
                ('master_binlog_file', models.CharField(max_length=30)),
                ('master_binlog_pos', models.CharField(max_length=30)),
                ('slave_sql_running_state', models.CharField(max_length=100)),
                ('create_time', models.DateTimeField(default=django.utils.timezone.now)),
            ],
            options={
                'db_table': 'mysql_replication_his',
            },
        ),
        migrations.AlterIndexTogether(
            name='mysql_replication',
            index_together=set([('db_ip', 'db_port')]),
        ),
    ]
