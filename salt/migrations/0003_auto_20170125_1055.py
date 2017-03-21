# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('salt', '0002_auto_20170125_1040'),
    ]

    operations = [
        migrations.AlterField(
            model_name='saltrecord',
            name='arg',
            field=models.TextField(),
        ),
    ]
