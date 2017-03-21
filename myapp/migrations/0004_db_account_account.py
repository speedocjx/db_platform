# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('myapp', '0003_auto_20161116_2242'),
    ]

    operations = [
        migrations.AddField(
            model_name='db_account',
            name='account',
            field=models.ManyToManyField(to=settings.AUTH_USER_MODEL),
        ),
    ]
