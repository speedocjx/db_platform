# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('myapp', '0039_auto_20170424_1537'),
    ]

    operations = [
        migrations.CreateModel(
            name='Tb_blacklist',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('tbname', models.CharField(max_length=255)),
                ('db', models.OneToOneField(to='myapp.Db_name')),
                ('user_permit', models.ManyToManyField(to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'db_table': 'tb_blacklist',
            },
        ),
    ]
