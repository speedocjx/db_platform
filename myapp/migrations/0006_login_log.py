# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0005_auto_20161125_1722'),
    ]

    operations = [
        migrations.CreateModel(
            name='Login_log',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('user', models.CharField(max_length=35)),
                ('ipaddr', models.CharField(max_length=35)),
                ('action', models.CharField(max_length=20)),
                ('create_time', models.DateTimeField(db_index=True)),
                ('login_time', models.DateTimeField()),
            ],
        ),
    ]
