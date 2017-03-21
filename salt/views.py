#coding=UTF-8
from django.shortcuts import render,render_to_response
from django.http import HttpResponse,HttpResponseRedirect,StreamingHttpResponse
import saltapi
import json
from django.contrib.auth.decorators import login_required,permission_required

# Create your views here.

@login_required(login_url='/accounts/login/')
@permission_required('myapp.can_oper_saltapi', login_url='/')
def salt_exec(request):
    return render(request, 'exec.html', locals())

@login_required(login_url='/accounts/login/')
@permission_required('myapp.can_oper_saltapi', login_url='/')
def execute(request):
    if request.method == 'POST':
        try:
            tgt = request.POST.get('tgt', "")
            # fun = request.POST.get('fun', "cmd.run")
            fun = "cmd.run"

            arg = request.POST.get('arg', 'none_arg')
            sapi = saltapi.SaltAPI()
            isgp = int(request.POST.get('isgroup', "0"))

            jid_auto = sapi.asyncMasterToMinion(tgt=tgt, fun=fun, arg=arg,group=isgp)
            saltapi.record_salt(request.user.username,jid_auto,fun,tgt,arg)
        except Exception,e:
            print e
    # context = {'jid_auto': ''}
    # tgt = request.POST.get('tgt', "")
    # fun = request.POST.get('fun', "cmd.run")
    # arg = request.POST.get('arg', "")
    return render_to_response('auto_execute.html', locals())

@login_required(login_url='/accounts/login/')
@permission_required('myapp.can_oper_saltapi', login_url='/')
def getjobinfo(request):
    context = {}
    jid_auto = request.GET['jid_auto']
    # print jid_auto
    if jid_auto:
        where = int(request.GET.get('where','12376894567235'))
        if where == 12376894567235:
            result = '/salt/api/getjobinfo?jid_auto=%s&where=%s' % (jid_auto,0)
            return HttpResponse(result)
        else:
            hosts_result, host_result = saltapi.salt_query("select id,success,replace(replace(`return`,'\\\\n','</br>'),'\\\\t','&nbsp') from salt.salt_returns where jid='%s' limit %s,10000;" % (jid_auto,where) )
            # cursor = connection.cursor()
            # host_result = cursor.execute()
            # hosts_result = cursor.fetchall()
            where = len(hosts_result) + where
            result = []
            for host_result in hosts_result:
                # print "host_result"
                # print host_result
                if host_result[2]:
                    result.append(u'host:%s&nbsp;&nbsp;&nbsp;state:%s<br><pre>%s</pre><br>' % (host_result[0],host_result[1],host_result[2].strip('"')))
                else :
                    if host_result[1]:
                        result.append(u'host:%s&nbsp;&nbsp;&nbsp;state:%s<br/><pre>执行成功，但该命令无返回结果</pre><br/>' % (host_result[0],host_result[1]))
                    else :
                        result.append(u'host:%s&nbsp;&nbsp;&nbsp;state:%s<br/><pre>执行失败！</pre><br/>' % (host_result[0],host_result[1]))
            context = {
                "where":where,
                "result":result
            }
        return HttpResponse(json.dumps(context))

@login_required(login_url='/accounts/login/')
@permission_required('myapp.can_oper_saltapi', login_url='/')
def hardware_info(request):
    try:
        if request.method == 'POST':
            se_host = request.POST.get('search','none')
            isgp = int(request.POST.get('isgroup', "0"))
            up_host = saltapi.get_host_list(se_host, isgp)
            sapi = saltapi.SaltAPI()
            # up_host = sapi.runner_status('status')['up']
            jyp = []
            disk_all = {}
            for hostname in up_host:
                info_all = sapi.remote_noarg_execution_sin(hostname, 'grains.items')

                disk_use = sapi.remote_noarg_execution_sin(hostname, 'disk.usage')

                for key in disk_use:
                    if disk_use[key]['capacity'] is None:
                        continue
                    disk_info = {key: int(disk_use[key]['capacity'][:-1])}
                    disk_all.update(disk_info)
                    disk_dic = {'disk': disk_all}
                    info_all.update(disk_dic)
                disk_all = {}
                jyp += [info_all]
    except Exception,e:
        print e
    return render(request, 'hardware_info.html', locals())

@login_required(login_url='/accounts/login/')
@permission_required('myapp.can_oper_saltapi', login_url='/')
def key_con(request):
    sapi = saltapi.SaltAPI()

    if request.POST:
        if request.POST.has_key('accept'):
            hostname = request.POST.get("accept")
            sapi.accept_key(hostname)
        elif request.POST.has_key('delete'):
            hostname = request.POST.get("delete")
            sapi.delete_key(hostname)
        elif request.POST.has_key('reject'):
            hostname = request.POST.get("reject")
            sapi.reject_key(hostname)
        elif request.POST.has_key('listall'):
            keys_all = sapi.list_all_key()
            return render(request, 'key_manager.html', locals())
        keys_all = sapi.list_all_key()
        return render(request, 'key_manager.html', locals())

    return  render(request,'key_manager.html',locals())


def hist_salt(request):


    return render(request, 'hist_task.html', locals())