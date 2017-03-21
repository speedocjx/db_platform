# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('myapp', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Db_account',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('user', models.CharField(max_length=30)),
                ('passwd', models.CharField(max_length=30)),
                ('role', models.CharField(default='all', max_length=30, choices=[('read', 'read'), ('write', 'write'), ('all', 'all')])),
                ('tags', models.CharField(max_length=30)),
            ],
        ),
        migrations.CreateModel(
            name='Db_instance',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('ip', models.CharField(max_length=30)),
                ('port', models.CharField(max_length=10)),
                ('role', models.CharField(max_length=30, choices=[('read', 'read'), ('write', 'write'), ('all', 'all')])),
            ],
        ),
        migrations.CreateModel(
            name='Db_name',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('dbtag', models.CharField(unique=True, max_length=30)),
                ('dbname', models.CharField(max_length=30)),
                ('account', models.ManyToManyField(to=settings.AUTH_USER_MODEL)),
                ('instance', models.ManyToManyField(to='myapp.Db_instance')),
            ],
        ),
        migrations.CreateModel(
            name='Incep_error_log',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('myid', models.IntegerField()),
                ('stage', models.CharField(max_length=20)),
                ('errlevel', models.IntegerField()),
                ('stagestatus', models.CharField(max_length=40)),
                ('errormessage', models.TextField()),
                ('sqltext', models.TextField()),
                ('affectrow', models.IntegerField()),
                ('sequence', models.CharField(max_length=30)),
                ('backup_db', models.CharField(max_length=100)),
                ('execute_time', models.CharField(max_length=20)),
                ('sqlsha', models.CharField(max_length=50)),
                ('create_time', models.DateTimeField(db_index=True)),
                ('finish_time', models.DateTimeField()),
            ],
        ),
        migrations.CreateModel(
            name='Oper_log',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('user', models.CharField(max_length=35)),
                ('ipaddr', models.CharField(max_length=35)),
                ('dbtag', models.CharField(max_length=35)),
                ('dbname', models.CharField(max_length=40)),
                ('sqltext', models.TextField()),
                ('sqltype', models.CharField(max_length=20)),
                ('create_time', models.DateTimeField(db_index=True)),
                ('login_time', models.DateTimeField()),
            ],
        ),
        migrations.CreateModel(
            name='Task',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('user', models.CharField(max_length=35)),
                ('dbtag', models.CharField(max_length=35)),
                ('sqltext', models.TextField()),
                ('create_time', models.DateTimeField(db_index=True)),
                ('update_time', models.DateTimeField()),
                ('status', models.CharField(max_length=20, db_index=True)),
                ('sqlsha', models.TextField()),
                ('sche_time', models.DateTimeField(default='2199-01-01 00:00:00', db_index=True)),
            ],
        ),
        migrations.CreateModel(
            name='Upload',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('username', models.CharField(max_length=40)),
                ('filename', models.FileField(upload_to='upload_sql')),
            ],
        ),
        migrations.CreateModel(
            name='User_profile',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('select_limit', models.IntegerField(default=200)),
                ('export_limit', models.IntegerField(default=200)),
                ('user', models.OneToOneField(to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'permissions': (('can_mysql_query', 'can see mysql_query view'), ('can_log_query', 'can see log_query view'), ('can_see_execview', 'can see mysql exec view'), ('can_export', 'can export csv'), ('can_insert_mysql', 'can insert mysql'), ('can_update_mysql', 'can update mysql'), ('can_delete_mysql', 'can delete mysql'), ('can_create_mysql', 'can create mysql'), ('can_drop_mysql', 'can drop mysql'), ('can_truncate_mysql', 'can truncate mysql'), ('can_alter_mysql', 'can alter mysql'), ('can_admin_task', 'can admin task')),
            },
        ),
        migrations.AlterIndexTogether(
            name='oper_log',
            index_together=set([('dbtag', 'sqltype', 'create_time')]),
        ),
        migrations.AddField(
            model_name='db_account',
            name='dbname',
            field=models.ManyToManyField(to='myapp.Db_name'),
        ),
    ]
