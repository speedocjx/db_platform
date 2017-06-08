# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0039_auto_20170424_1537'),
    ]

    operations = [
        migrations.AlterField(
            model_name='db_account',
            name='account',
            field=models.ManyToManyField(db_constraint=False, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='db_account',
            name='dbname',
            field=models.ManyToManyField(db_constraint=False, to='myapp.Db_name'),
        ),
        migrations.AlterField(
            model_name='db_group',
            name='account',
            field=models.ManyToManyField(db_constraint=False, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='db_group',
            name='dbname',
            field=models.ManyToManyField(db_constraint=False, to='myapp.Db_name'),
        ),
        migrations.AlterField(
            model_name='db_name',
            name='account',
            field=models.ManyToManyField(db_constraint=False, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='db_name',
            name='instance',
            field=models.ManyToManyField(db_constraint=False, to='myapp.Db_instance'),
        ),
        migrations.AlterField(
            model_name='mysql_monitor',
            name='account',
            field=models.ForeignKey(to='myapp.Db_account', db_constraint=False),
        ),
        migrations.AlterField(
            model_name='mysql_monitor',
            name='instance',
            field=models.OneToOneField(to='myapp.Db_instance', db_constraint=False),
        ),
        migrations.AlterField(
            model_name='user_profile',
            name='user',
            field=models.OneToOneField(to=settings.AUTH_USER_MODEL, db_constraint=False),
        ),
    ]
