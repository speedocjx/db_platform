from django.db import models

# Create your models here.
def mon_set(request):
    dblist = MySQL_monitor.objects.all().order_by('id')
    return render(request,'previliges/mon_set.html',locals())