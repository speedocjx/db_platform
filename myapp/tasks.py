from celery import task
import datetime
from django.contrib.auth.models import User
from myapp.models import User_profile,Db_account,Db_instance,Oper_log,Task,Incep_error_log
from myapp.include import inception as incept,binlog2sql
from django.core.mail import EmailMessage,send_mail,EmailMultiAlternatives
from django.template import loader
from myapp.include.encrypt import prpcrypt
from mypro.settings import EMAIL_SENDER
@task
def process_runtask(hosttag,sqltext,mytask):
    flag = (1 if mytask.backup_status == 1 else 3)
    results,col,tar_dbname = incept.inception_check(hosttag,sqltext,flag)
    status='executed'
    c_time = mytask.create_time
    mytask.update_time = datetime.datetime.now()
    if flag == 1:
        mytask.backup_status=2
    mytask.save()
    for row in results:
        try:
            inclog = Incep_error_log(myid=row[0],stage=row[1],errlevel=row[2],stagestatus=row[3],errormessage=row[4],\
                         sqltext=row[5],affectrow=row[6],sequence=row[7],backup_db=row[8],execute_time=row[9],sqlsha=row[10],\
                         create_time=c_time,finish_time=mytask.update_time)
            inclog.save()
            #if some error occured in inception_check stage
        except Exception,e:
            inclog = Incep_error_log(myid=999,stage='',errlevel=999,stagestatus='',errormessage=row[0],\
                         sqltext=e,affectrow=999,sequence='',backup_db='',execute_time='',sqlsha='',\
                         create_time=c_time,finish_time=mytask.update_time)
            inclog.save()
        if (int(row[2])!=0):
            status='executed failed'
            #record error message of incept exec
    mytask.status = status
    mytask.save()
    sendmail_task.delay(mytask)

@task
def parse_binlog(insname,binname,begintime,tbname,dbselected,username,countnum,flash_back):
    flag = True
    pc = prpcrypt()
    for a in insname.db_name_set.all():
        for i in a.db_account_set.all():
            if i.role == 'admin':
                tar_username = i.user
                tar_passwd = pc.decrypt(i.passwd)
                flag = False
                break
        if flag == False:
            break
    connectionSettings = {'host': insname.ip, 'port': int(insname.port), 'user': tar_username, 'passwd': tar_passwd}
    binlogsql = binlog2sql.Binlog2sql(connectionSettings=connectionSettings, startFile=binname,
                                      startPos=4, endFile='', endPos=0,
                                      startTime=begintime, stopTime='', only_schemas=dbselected,
                                      only_tables=tbname, nopk=False, flashback=flash_back, stopnever=False,countnum=countnum)
    binlogsql.process_binlog()
    sqllist = binlogsql.sqllist
    sendmail_sqlparse.delay(username, dbselected, tbname, sqllist,flash_back)


def parse_binlogfirst(insname,binname,countnum):
    flag = True
    pc = prpcrypt()
    for a in insname.db_name_set.all():
        for i in a.db_account_set.all():
            if i.role == 'admin':
                tar_username = i.user
                tar_passwd = pc.decrypt(i.passwd)
                flag = False
                break
        if flag == False:
            break
    connectionSettings = {'host': insname.ip, 'port': int(insname.port), 'user': tar_username, 'passwd': tar_passwd}
    binlogsql = binlog2sql.Binlog2sql(connectionSettings=connectionSettings, startFile=binname,
                                      startPos=4, endFile='', endPos=0,
                                      startTime='', stopTime='', only_schemas='',
                                      only_tables='', nopk=False, flashback=False, stopnever=False,countnum=countnum)
    binlogsql.process_binlog()
    sqllist = binlogsql.sqllist
    return sqllist




@task
def sendmail_sqlparse(user,db,tb,sqllist,flashback):
    mailto=[]
    if flashback==True:
        title = "BINLOG PARSE (UNDO) FOR "+ db + "." + tb
    else:
        title = "BINLOG PARSE (REDO) FOR " + db + "." + tb
    mailto.append(User.objects.get(username=user).email)
    html_content = loader.render_to_string('include/mail_template.html', locals())
    sendmail(title, mailto, html_content)

@task
def sendmail_task(task):
    # tmp=u'x'
    try:
        mailto = []
        for i in User_profile.objects.filter(task_email__gt=0):
            if len(i.user.email) > 0:
                mailto.append(i.user.email)
        # if type(task) != type(tmp):
        if task.status != 'NULL':
            # del tmp
            mailto.append(User.objects.get(username=task.user).email)
            result_status = Incep_error_log.objects.filter(create_time=task.create_time).filter(finish_time=task.update_time).order_by("-myid")
            title = 'Task ID:' + str(task.id) + '  has finished'
        else:
            title = "You have received new task!"
            tmp = task
        html_content = loader.render_to_string('include/mail_template.html', locals())
        sendmail(title, mailto, html_content)

    except Exception ,e:
        print e

@task
def sendmail_forget(sendto,title,message):
    mailto=[]
    message=message
    mailto.append(sendto)
    html_content = loader.render_to_string('include/mail_template.html', locals())
    sendmail(title, mailto, html_content)


def sendmail (title,mailto,html_content):
    try:
        msg = EmailMultiAlternatives(title, html_content, EMAIL_SENDER, mailto)
        msg.attach_alternative(html_content, "text/html")
        msg.send()
    except Exception,e:
        print e







def task_run(idnum,request):
    while 1:
        try:
            task = Task.objects.get(id=idnum)
        except:
            continue
        break
    if task.status!='executed' and task.status!='running' and task.status!='NULL':
        hosttag = task.dbtag
        sql = task.sqltext
        mycreatetime = task.create_time
        incept.log_incep_op(sql,hosttag,request,mycreatetime)
        status='running'
        task.status = status
        task.operator  = request.user.username
        task.update_time = datetime.datetime.now()
        task.save()
        process_runtask.delay(hosttag,sql,task)
        return ''
    elif task.status=='NULL':
        return 'PLEASE CHECK THE SQL FIRST'
    else:
        return 'Already executed or in running'
