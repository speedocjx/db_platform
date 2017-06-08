# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('blacklist', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='tb_blacklist',
            name='user_permit',
            field=models.ManyToManyField(db_constraint=False, to=settings.AUTH_USER_MODEL),
        ),
    ]
