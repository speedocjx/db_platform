from django.shortcuts import render
from myapp.models import Db_group,Db_name,Db_account,Db_instance,Oper_log,Upload,Task,MySQL_monitor
from myapp.include import monitor
from django.http import HttpResponse,HttpResponseRedirect,StreamingHttpResponse,JsonResponse


# Create your views here.
def mon_set(request):
    dblist = MySQL_monitor.objects.all().order_by('id')
    return render(request,'mon_set.html',locals())

def mon_change(request):
    ins_list = Db_instance.objects.all().order_by('ip')
    acc_list = Db_account.objects.all().order_by('tags')
    myid = int(request.GET['dbid'])
    edit_db = MySQL_monitor.objects.get(id=myid)
    return render(request,'mon_edit.html',locals())

def mon_delete(request):
    myid = int(request.GET['dbid'])
    print MySQL_monitor.objects.get(id=myid)
    return HttpResponseRedirect("/monitor/mon_set/")
