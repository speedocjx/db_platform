# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0026_auto_20170324_1629'),
    ]

    operations = [
        migrations.CreateModel(
            name='MySQL_monitor',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('tag', models.CharField(max_length=20)),
                ('check_longsql', models.SmallIntegerField(default=0)),
                ('longsql_time', models.SmallIntegerField(default=1200)),
                ('check_active', models.SmallIntegerField(default=0)),
                ('active_threshold', models.SmallIntegerField(default=30)),
                ('mail_to', models.CharField(max_length=255)),
                ('account', models.OneToOneField(to='myapp.Db_account')),
                ('instance', models.OneToOneField(to='myapp.Db_instance')),
            ],
            options={
                'db_table': 'mysql_monitor',
            },
        ),
    ]
