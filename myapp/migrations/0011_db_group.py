# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('myapp', '0010_auto_20161126_1725'),
    ]

    operations = [
        migrations.CreateModel(
            name='Db_group',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('groupname', models.CharField(max_length=30)),
                ('account', models.ManyToManyField(to=settings.AUTH_USER_MODEL)),
                ('dbname', models.ManyToManyField(to='myapp.Db_name')),
            ],
        ),
    ]
