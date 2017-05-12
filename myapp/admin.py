from django.contrib import admin
from myapp.models import Db_name,Db_account,Db_instance,User_profile,MySQL_monitor,Tb_blacklist
from django.contrib.auth.models import User

admin.site.register(Db_name)
admin.site.register(Db_account)
admin.site.register(Db_instance)
admin.site.register(MySQL_monitor)
admin.site.register(Tb_blacklist)
# admin.site.register(Db_group)
admin.site.register(User_profile)
# Register your models here.
