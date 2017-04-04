
from django.db import models
import django.utils.timezone as timezone
# Create your models here.
class Mysql_processlist(models.Model):
    db_ip = models.CharField(max_length=20)
    db_port = models.SmallIntegerField()
    conn_id = models.CharField(max_length=30)
    user = models.CharField(max_length=32)
    host = models.CharField(max_length=64)
    db = models.CharField(max_length=64)
    command = models.CharField(max_length=16)
    time = models.IntegerField()
    state = models.CharField(null=True,max_length=64)
    info = models.TextField(null=True)
    create_time = models.DateTimeField(default=timezone.now)
    class Meta:
        db_table = 'mysql_processlist'