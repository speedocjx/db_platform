from django.shortcuts import render
from monitor.models import MysqlStatus,Mysql_replication
from myapp.models import Db_account,Db_instance,MySQL_monitor
from django.http import HttpResponse,HttpResponseRedirect,StreamingHttpResponse,JsonResponse
from django.contrib.auth.decorators import login_required,permission_required
from django.core.paginator import Paginator, InvalidPage, EmptyPage
from myapp.include.scheduled import get_dupreport
from django.contrib.auth.models import User

# Create your views here.
@login_required(login_url='/accounts/login/')
@permission_required('myapp.can_see_mysqladmin', login_url='/')
def mon_set(request):
    page_size = 10
    all_record = MySQL_monitor.objects.all().order_by('id')
    paginator = Paginator(all_record, page_size)
    try:
        page = int(request.GET.get('page', 1))
    except ValueError:
        page = 1
    try:
        posts = paginator.page(page)
    except (EmptyPage, InvalidPage):
        posts = paginator.page(paginator.num_pages)

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
        try:
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
                edit_db.replchannel = request.POST['slavechannel_set']
                edit_db.check_connections = int(request.POST['connection_set'])
                edit_db.connection_threshold = int(request.POST['connectiontre_set'])
                edit_db.check_slave =  int(request.POST['slave_set'])
                edit_db.check_delay = int(request.POST['slavedelay_set'])
                edit_db.delay_threshold = int(request.POST['slavedelaytre_set'])
                edit_db.alarm_times = int(request.POST['alarmtime_set'])
                edit_db.alarm_interval = int(request.POST['alarminterval_set'])

                edit_db.mail_to = request.POST['mailset']
                edit_db.save()
            elif request.POST.has_key('delete'):
                myid = int(request.POST['set'])
                delete_mon(myid)
                return HttpResponseRedirect("/monitor/mon_set/")
            elif request.POST.has_key('create'):
                if request.POST['ins_set'] !='' and request.POST['acc_set']!='':
                    edit_db = MySQL_monitor(instance=Db_instance.objects.get(id=int(request.POST['ins_set'])),\
                                            account=Db_account.objects.get(id=int(request.POST['acc_set'])),\
                                            tag=request.POST['tagset'],monitor=int(request.POST['monitor_set']),\
                                            check_longsql=int(request.POST['longsql_set']),longsql_autokill=int(request.POST['autokill_set']),\
                                            longsql_time=int(request.POST['longthre_set']),check_active=int(request.POST['activesql_set']),\
                                            active_threshold=int(request.POST['activetre_set']),check_connections=int(request.POST['connection_set']), \
                                            connection_threshold=int(request.POST['connectiontre_set']),check_slave=int(request.POST['slave_set']), \
                                            check_delay=int(request.POST['slavedelay_set']),delay_threshold=int(request.POST['slavedelaytre_set']), \
                                            alarm_times=int(request.POST['alarmtime_set']),alarm_interval=int(request.POST['alarminterval_set']), \
                                            replchannel=request.POST['slavechannel_set'],mail_to=request.POST['mailset'])
                    edit_db.save()
        except Exception,e:
            print e
            info = "set failed"
    return render(request,'mon_edit.html',locals())

@login_required(login_url='/accounts/login/')
@permission_required('myapp.can_see_mysqladmin', login_url='/')
def mon_delete(request):
    myid = int(request.GET['dbid'])
    delete_mon(myid)
    return HttpResponseRedirect("/monitor/mon_set/")

def delete_mon(id):
    db = MySQL_monitor.objects.get(id=id)
    MysqlStatus.objects.filter(db_ip=db.instance.ip,db_port=db.instance.port).delete()
    Mysql_replication.objects.filter(db_ip=db.instance.ip,db_port=db.instance.port).delete()
    MySQL_monitor.objects.get(id=id).delete()

@login_required(login_url='/accounts/login/')
@permission_required('myapp.can_see_mysqladmin', login_url='/')
def mysql_status(request):
    page_size = 15
    all_record = MysqlStatus.objects.order_by('db_ip')
    paginator = Paginator(all_record, page_size)
    try:
        page = int(request.GET.get('page', 1))
    except ValueError:
        page = 1
    try:
        posts = paginator.page(page)
    except (EmptyPage, InvalidPage):
        posts = paginator.page(paginator.num_pages)
    return render(request, 'mysql_status.html', locals())


@login_required(login_url='/accounts/login/')
@permission_required('myapp.can_see_mysqladmin', login_url='/')
def batch_add(request):

    return render(request, 'batch_add.html', locals())


def test_tb(request):
    print request.user.email
    get_dupreport.delay('mysql-lepus',request.user.email)
    return render(request, 'batch_add.html', locals())


