from __future__ import unicode_literals
from django.contrib.auth.models import User
from django.db import models

read_write = (
    ('read', 'read'),
    ('write', 'write'),
    ('all','all'),
    ('idle','idle'),
)
read_write_account = (
    ('read', 'read'),
    ('write', 'write'),
    ('all','all'),
    ('admin','admin'),
)
db_type = (
    ('mysql', 'mysql'),
    ('mongodb', 'write'),
)

class Db_instance(models.Model):
    ip = models.CharField(max_length=30)
    port = models.CharField(max_length=10)
    role =  models.CharField(max_length=30,choices=read_write, )
    db_type = models.CharField(max_length=30,default='mysql')
    def __unicode__(self):
        return u'%s %s %s' % (self.ip, self.role, self.db_type)
    class Meta:
        unique_together = ("ip","port")


class Db_name (models.Model):
    dbtag = models.CharField(max_length=30,unique=True)
    dbname = models.CharField(max_length=30)
    instance = models.ManyToManyField(Db_instance)
    account = models.ManyToManyField(User)
    def __unicode__(self):
        return u'%s %s' % (self.dbtag, self.dbname)


class Db_account(models.Model):
    user = models.CharField(max_length=30)
    passwd = models.CharField(max_length=30)
    role =  models.CharField(max_length=30,choices=read_write_account,default='all')
    tags = models.CharField(max_length=30,db_index=True)
    dbname = models.ManyToManyField(Db_name)
    account = models.ManyToManyField(User)
    def __unicode__(self):
        return  u'%s %s' % ( self.tags,self.role)

class Db_group(models.Model):
    groupname = models.CharField(max_length=30,unique=True)
    dbname = models.ManyToManyField(Db_name)
    account = models.ManyToManyField(User)
    def __unicode__(self):
        return self.groupname

class Oper_log(models.Model):
    user = models.CharField(max_length=35)
    ipaddr = models.CharField(max_length=35)
    dbtag = models.CharField(max_length=35)
    dbname = models.CharField(max_length=40)
    sqltext = models.TextField()
    sqltype = models.CharField(max_length=20)
    create_time = models.DateTimeField(db_index=True)
    login_time = models.DateTimeField()
    def __unicode__(self):
        return self.dbtag
    class Meta:
        index_together = [["dbtag","sqltype", "create_time"],]

class Login_log(models.Model):
    user = models.CharField(max_length=35)
    ipaddr = models.CharField(max_length=35)
    action = models.CharField(max_length=20)
    create_time = models.DateTimeField(db_index=True)

# class Task_scheduler(models.Model):
#     task = models.OneToOneField(Task)
#     appoint_time = models.DateTimeField(db_index=True)
#     def __unicode__(self):
#         return  self.task.id


class User_profile(models.Model):
    user = models.OneToOneField(User)
    select_limit = models.IntegerField(default=200)
    export_limit = models.IntegerField(default=200)
    task_email = models.IntegerField(db_index=True)
    def __unicode__(self):
        return  self.user.username
    class Meta:
        permissions =(('can_mysql_query','can see mysql_query view'),
                      ('can_log_query','can see log_query view'),
                      ('can_see_execview','can see mysql exec view'),
                      ('can_see_inception', 'can see inception view'),
                      ('can_see_metadata', 'can see meta_data view'),
                      ('can_see_mysqladmin', 'can see mysql_admin view'),
                      ('can_export','can export csv'),
                      ('can_insert_mysql','can insert mysql'),
                      ('can_update_mysql','can update mysql'),
                      ('can_delete_mysql','can delete mysql'),
                      ('can_create_mysql','can create mysql'),
                      ('can_drop_mysql','can drop mysql'),
                      ('can_truncate_mysql','can truncate mysql'),
                      ('can_alter_mysql','can alter mysql'),
                      ('can_query_mongo', 'can query mongo'),
                      ('can_see_taskview', 'can see task view'),
                      ('can_admin_task','can admin task'),
                      ('can_delete_task', 'can delete task'),
                      ('can_update_task', 'can update task'),
                      ('can_query_pri', 'can query pri'),
                      ('can_set_pri', 'can set pri'),
                      ('can_oper_saltapi', 'can oper saltapi'),
                      )

class Upload(models.Model):
    username = models.CharField(max_length = 40)
    filename = models.FileField(upload_to = 'upload_sql')
    def __unicode__(self):
        return self.username
# Create your models here.
class Task(models.Model):
    user = models.CharField(max_length=35)
    dbtag = models.CharField(max_length=35)
    sqltext = models.TextField()
    create_time = models.DateTimeField(db_index=True)
    update_time = models.DateTimeField()
    status = models.CharField(max_length=20,db_index=True)
    sqlsha =  models.TextField()
    sche_time = models.DateTimeField(db_index=True,default='2199-01-01 00:00:00')
    specification = models.CharField(max_length=100,default='')
    operator = models.CharField(max_length=35, default='')
    def __unicode__(self):
        return self.dbtag

class Incep_error_log(models.Model):
    myid = models.IntegerField()
    stage = models.CharField(max_length= 20)
    errlevel = models.IntegerField()
    stagestatus = models.CharField(max_length=40)
    errormessage = models.TextField()
    sqltext = models.TextField()
    affectrow = models.IntegerField()
    sequence = models.CharField(max_length=30)
    backup_db = models.CharField(max_length=100)
    execute_time = models.CharField(max_length=20)
    sqlsha = models.CharField(max_length=50)
    create_time = models.DateTimeField(db_index=True)
    finish_time = models.DateTimeField()
