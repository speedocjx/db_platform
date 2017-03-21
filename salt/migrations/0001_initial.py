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
                ('user', models.CharField(max_length=30)),
                ('operation', models.CharField(max_length=50)),
                ('jid', models.CharField(max_length=255, db_index=True)),
                ('return_field', models.TextField(db_column=b'return')),
                ('create_time', models.DateTimeField()),
            ],
            options={
                'db_table': 'salt_record',
            },
        ),
    ]
