# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('monitor', '0010_auto_20170405_1429'),
    ]

    operations = [
        migrations.AlterField(
            model_name='mysql_replication',
            name='current_binlog_file',
            field=models.CharField(max_length=30, null=True),
        ),
        migrations.AlterField(
            model_name='mysql_replication',
            name='current_binlog_pos',
            field=models.CharField(max_length=30, null=True),
        ),
        migrations.AlterField(
            model_name='mysql_replication',
            name='delay',
            field=models.CharField(max_length=20, null=True),
        ),
        migrations.AlterField(
            model_name='mysql_replication',
            name='gtid_mode',
            field=models.CharField(max_length=10, null=True),
        ),
        migrations.AlterField(
            model_name='mysql_replication',
            name='master_binlog_file',
            field=models.CharField(max_length=30, null=True),
        ),
        migrations.AlterField(
            model_name='mysql_replication',
            name='master_binlog_pos',
            field=models.CharField(max_length=30, null=True),
        ),
        migrations.AlterField(
            model_name='mysql_replication',
            name='master_port',
            field=models.CharField(max_length=20, null=True),
        ),
        migrations.AlterField(
            model_name='mysql_replication',
            name='master_server',
            field=models.CharField(max_length=30, null=True),
        ),
        migrations.AlterField(
            model_name='mysql_replication',
            name='read_only',
            field=models.CharField(max_length=10, null=True),
        ),
        migrations.AlterField(
            model_name='mysql_replication',
            name='slave_io_run',
            field=models.CharField(max_length=20, null=True),
        ),
        migrations.AlterField(
            model_name='mysql_replication',
            name='slave_sql_run',
            field=models.CharField(max_length=20, null=True),
        ),
        migrations.AlterField(
            model_name='mysql_replication',
            name='slave_sql_running_state',
            field=models.CharField(max_length=100, null=True),
        ),
        migrations.AlterField(
            model_name='mysql_replication_his',
            name='current_binlog_file',
            field=models.CharField(max_length=30, null=True),
        ),
        migrations.AlterField(
            model_name='mysql_replication_his',
            name='current_binlog_pos',
            field=models.CharField(max_length=30, null=True),
        ),
        migrations.AlterField(
            model_name='mysql_replication_his',
            name='delay',
            field=models.CharField(max_length=20, null=True),
        ),
        migrations.AlterField(
            model_name='mysql_replication_his',
            name='gtid_mode',
            field=models.CharField(max_length=10, null=True),
        ),
        migrations.AlterField(
            model_name='mysql_replication_his',
            name='master_binlog_file',
            field=models.CharField(max_length=30, null=True),
        ),
        migrations.AlterField(
            model_name='mysql_replication_his',
            name='master_binlog_pos',
            field=models.CharField(max_length=30, null=True),
        ),
        migrations.AlterField(
            model_name='mysql_replication_his',
            name='master_port',
            field=models.CharField(max_length=20, null=True),
        ),
        migrations.AlterField(
            model_name='mysql_replication_his',
            name='master_server',
            field=models.CharField(max_length=30, null=True),
        ),
        migrations.AlterField(
            model_name='mysql_replication_his',
            name='read_only',
            field=models.CharField(max_length=10, null=True),
        ),
        migrations.AlterField(
            model_name='mysql_replication_his',
            name='slave_io_run',
            field=models.CharField(max_length=20, null=True),
        ),
        migrations.AlterField(
            model_name='mysql_replication_his',
            name='slave_sql_run',
            field=models.CharField(max_length=20, null=True),
        ),
        migrations.AlterField(
            model_name='mysql_replication_his',
            name='slave_sql_running_state',
            field=models.CharField(max_length=100, null=True),
        ),
    ]
