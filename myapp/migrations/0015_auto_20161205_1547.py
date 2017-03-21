# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0014_auto_20161201_2258'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='user_profile',
            options={'permissions': (('can_mysql_query', 'can see mysql_query view'), ('can_log_query', 'can see log_query view'), ('can_see_execview', 'can see mysql exec view'), ('can_see_inception', 'can see inception view'), ('can_export', 'can export csv'), ('can_insert_mysql', 'can insert mysql'), ('can_update_mysql', 'can update mysql'), ('can_delete_mysql', 'can delete mysql'), ('can_create_mysql', 'can create mysql'), ('can_drop_mysql', 'can drop mysql'), ('can_truncate_mysql', 'can truncate mysql'), ('can_alter_mysql', 'can alter mysql'), ('can_see_taskview', 'can see task view'), ('can_admin_task', 'can admin task'), ('can_delete_task', 'can delete task'), ('can_update_task', 'can update task'), ('can_query_pri', 'can query pri'), ('can_set_pri', 'can set pri'))},
        ),
    ]
