from django.shortcuts import render
from myapp.models import Db_group,Db_name,Db_account,Db_instance,Oper_log,Upload,Task,MySQL_monitor
from django.http import HttpResponse,HttpResponseRedirect,StreamingHttpResponse,JsonResponse
from django.contrib.auth.decorators import login_required,permission_required


# Create your views here.
@login_required(login_url='/accounts/login/')
@permission_required('myapp.can_see_mysqladmin', login_url='/')
def mon_set(request):
    dblist = MySQL_monitor.objects.all().order_by('id')
    return render(request,'mon_set.html',locals())

@login_required(login_url='/accounts/login/')
@permission_required('myapp.can_see_mysqladmin', login_url='/')
def mon_edit(request):
    ins_list = Db_instance.objects.all().order_by('ip')
    acc_list = Db_account.objects.all().order_by('tags')
    if request.method == 'GET':
        try:
            myid = int(request.GET['dbid'])
            edit_db = MySQL_monitor.objects.get(id=myid)
        except :
            pass

    elif request.method == 'POST':
        if request.POST.has_key('set'):
            myid = int(request.POST['set'])
            edit_db = MySQL_monitor.objects.get(id=myid)
            edit_db.tag = request.POST['tagset']
            edit_db.instance = Db_instance.objects.get(id=int(request.POST['ins_set']))
            edit_db.account = Db_account.objects.get(id=int(request.POST['acc_set']))
            edit_db.monitor = int(request.POST['monitor_set'])
            edit_db.check_longsql = int(request.POST['longsql_set'])
            edit_db.longsql_autokill = int(request.POST['autokill_set'])
            edit_db.longsql_time = int(request.POST['longthre_set'])
            edit_db.check_active = int(request.POST['activesql_set'])
            edit_db.active_threshold = int(request.POST['activetre_set'])
            edit_db.mail_to = request.POST['mailset']
            edit_db.save()
        elif request.POST.has_key('delete'):
            myid = int(request.POST['set'])
            MySQL_monitor.objects.get(id=myid).delete()
            return HttpResponseRedirect("/monitor/mon_set/")
        elif request.POST.has_key('create'):
            if request.POST['ins_set'] !='' and request.POST['acc_set']!='':
                edit_db = MySQL_monitor(instance=Db_instance.objects.get(id=int(request.POST['ins_set'])),\
                                        account=Db_account.objects.get(id=int(request.POST['acc_set'])),\
                                        tag=request.POST['tagset'],monitor=int(request.POST['monitor_set']),\
                                        check_longsql=int(request.POST['longsql_set']),longsql_autokill=int(request.POST['autokill_set']),\
                                        longsql_time=int(request.POST['longthre_set']),check_active=int(request.POST['activesql_set']),\
                                        active_threshold=int(request.POST['activetre_set']), \
                                        mail_to=request.POST['mailset'])
                edit_db.save()
    return render(request,'mon_edit.html',locals())

@login_required(login_url='/accounts/login/')
@permission_required('myapp.can_see_mysqladmin', login_url='/')
def mon_delete(request):
    myid = int(request.GET['dbid'])
    MySQL_monitor.objects.get(id=myid).delete()
    return HttpResponseRedirect("/monitor/mon_set/")
