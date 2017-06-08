from django.db import models
import django.utils.timezone as timezone

# Create your models here.


class Passwd_forget(models.Model):
    username = models.CharField(max_length=30)
    vc_value = models.CharField(max_length=40, db_index=True)
    is_valid = models.SmallIntegerField(default=1)
    create_time = models.DateTimeField(default=timezone.now)

    class Meta:
        index_together = ["username", "is_valid"]
