#!/bin/env python
#-*-coding:utf-8-*-
import MySQLdb,sys,string,time,datetime,uuid
from django.contrib.auth.models import User,Permission,ContentType,Group
from myapp.models import Db_name,Db_account,Db_instance,Oper_log,Login_log,Db_group
from myapp.form import LoginForm,Captcha

reload(sys)
sys.setdefaultencoding('utf8')
import ConfigParser
import smtplib
from email.mime.text import MIMEText
from email.message import Message
from email.header import Header




def get_item(data_dict,item):
    try:
       item_value = data_dict[item]
       return item_value
    except:
       return '-1'

def get_config(group,config_name):
    config = ConfigParser.ConfigParser()
    config.readfp(open('./myapp/etc/config.ini','r'))
    #config.readfp(open('../etc/config.ini','r'))
    config_value=config.get(group,config_name).strip(' ').strip('\'').strip('\"')
    return config_value

def filters(data):
    return data.strip(' ').strip('\n').strip('\br')

host = get_config('settings','host')
port = get_config('settings','port')
user = get_config('settings','user')
passwd = get_config('settings','passwd')
dbname = get_config('settings','dbname')
select_limit = int(get_config('settings','select_limit'))
export_limit = int(get_config('settings','export_limit'))
wrong_msg = get_config('settings','wrong_msg')
public_user = get_config('settings','public_user')

def mysql_query(sql,user=user,passwd=passwd,host=host,port=int(port),dbname=dbname,limitnum=select_limit):
    try:
        conn=MySQLdb.connect(host=host,user=user,passwd=passwd,port=int(port),connect_timeout=5,charset='utf8')
        conn.select_db(dbname)
        cursor = conn.cursor()
        count=cursor.execute(sql)
        index=cursor.description
        col=[]
        #get column name
        for i in index:
            col.append(i[0])
        #result=cursor.fetchall()
        result=cursor.fetchmany(size=int(limitnum))
        cursor.close()
        conn.close()
        return (result,col)
    except Exception,e:
        return([str(e)],''),['error']

#获取下拉菜单列表
def get_mysql_hostlist(username,tag='tag'):
    host_list=[]
    if (tag=='tag'):
        a = User.objects.get(username=username)
        #如果没有对应role='read'或者role='all'的account账号，则不显示在下拉菜单中
        for row in a.db_name_set.all().order_by("dbtag"):
            if row.db_account_set.all().filter(role__in=['read','all']):
                if row.instance.all().filter(role__in=['read','all']):
                    host_list.append(row.dbtag)
    elif (tag=='log'):
        for row in Db_name.objects.values('dbtag').distinct().order_by("dbtag"):
            host_list.append(row['dbtag'])
    elif (tag=='exec'):
        a = User.objects.get(username=username)
        #如果没有对应role='write'或者role='all'的account账号，则不显示在下拉菜单中
        for row in a.db_name_set.all().order_by("dbtag"):
            if row.db_account_set.all().filter(role__in=['write','all']):
        #排除只读实例
                if row.instance.all().filter(role__in=['write','all']):
                    host_list.append(row.dbtag)
    elif (tag == 'incept'):
        a = User.objects.get(username=username)
        for row in a.db_name_set.all().order_by("dbtag"):
            #find the account which is admin
            if row.db_account_set.all().filter(role='admin'):
                if row.instance.all().filter(role__in=['write','all']):
                #if row.instance.all().exclude(role='read'):
                    host_list.append(row.dbtag)
    elif (tag == 'meta'):
        for row in Db_name.objects.all().order_by("dbtag"):
            #find the account which is admin
            if row.db_account_set.all().filter(role='admin'):
                if row.instance.filter(role__in=['write','all','read']):
                    host_list.append(row.dbtag)
    return host_list

def get_op_type(methods='get'):
    #all表示所有种类
    op_list=['all','incept','truncate','drop','create','delete','update','insert','select','explain','alter','show']
    if (methods=='get'):
        return op_list

def get_mysql_data(hosttag,sql,useraccount,request,limitnum):
    #确认dbname
    a = Db_name.objects.filter(dbtag=hosttag)[0]
    #a = Db_name.objects.get(dbtag=hosttag)
    tar_dbname = a.dbname
    #如果instance中有备库role='read'，则选择从备库读取
    try:
        if a.instance.all().filter(role='read')[0]:
            tar_host = a.instance.all().filter(role='read')[0].ip
            tar_port = a.instance.all().filter(role='read')[0].port
    #如果没有设置或没有role=read，则选择第一个读到的all实例读取
    except Exception,e:
        tar_host = a.instance.filter(role='all')[0].ip
        tar_port = a.instance.filter(role='all')[0].port
        # tar_host = a.instance.all()[0].ip
        # tar_port = a.instance.all()[0].port
    for i in a.db_account_set.all():
        if i.role!='write' and i.role!='admin':
            # find the specified account for the user
            if i.account.all().filter(username=useraccount):
                tar_username = i.user
                tar_passwd = i.passwd
                break
    #not find specified account for the user ,specified the public account to the user
    if not vars().has_key('tar_username'):
        for i in a.db_account_set.all():
            if i.role != 'write' and i.role != 'admin':
                # find the specified account for the user
                if i.account.all().filter(username=public_user):
                    tar_username = i.user
                    tar_passwd = i.passwd
                    break
    #print tar_port+tar_passwd+tar_username+tar_host
    try:
        if (cmp(sql,wrong_msg)):
            log_mysql_op(useraccount,sql,tar_dbname,hosttag,request)
        results,col = mysql_query(sql,tar_username,tar_passwd,tar_host,tar_port,tar_dbname,limitnum)
    except Exception, e:
        #防止日志库记录失败，返回一个wrong_message
        results,col = ([str(e)],''),['error']
        #results,col = mysql_query(wrong_msg,user,passwd,host,int(port),dbname)
    return results,col,tar_dbname

#检查输入语句,并返回行限制数
def check_mysql_query(sqltext,user,type='select'):
    #根据user确定能够select或者export 的行数
    if (type=='export'):
        try :
            num = User.objects.get(username=user).user_profile.export_limit
        except Exception, e:
            num = export_limit
    elif (type=='select'):
        try :
            num = User.objects.get(username=user).user_profile.select_limit
        except Exception, e:
            num = select_limit
    num=str(num)
    limit = ' limit '+ num

    sqltext = sqltext.strip()
    sqltype = sqltext.split()[0].lower()
    list_type = ['select','show','desc','explain']
    #flag 1位有效 0为list_type中的无效值
    flag=0
    while True:
        sqltext = sqltext.strip()
        lastletter = sqltext[len(sqltext)-1]
        if (not cmp(lastletter,';')):
            sqltext = sqltext[:-1]
        else:
            break
    #判断语句中是否已经存在limit，has_limit 为0时说明原来语句中是有limit的
    try:
        has_limit = cmp(sqltext.split()[-2].lower(),'limit')
    except Exception,e:
        #prevent some input like '1' or 'ss' ...
        return wrong_msg, num

    for i in list_type:
        if (not cmp(i,sqltype)):
            flag=1
            break
    if (flag==1):
        if (sqltype =='select' and has_limit!=0):
            return sqltext+limit,num
        elif (sqltype =='select' and has_limit==0):
            if (int(sqltext.split()[-1])<= int(num) ):
                return sqltext,num
            else:
                tempsql=''
                numlimit=sqltext.split()[-1]
                for i in sqltext.split()[0:-1]:
                    tempsql=tempsql+i+' '
                return tempsql+num,num
        else:
            return sqltext,num
    else:
        return wrong_msg,num

#记录用户所有操作
def log_mysql_op(user,sqltext,mydbname,dbtag,request):
    user = User.objects.get(username=user)
    #lastlogin = user.last_login+datetime.timedelta(hours=8)
    #create_time = datetime.datetime.now()+datetime.timedelta(hours=8)
    lastlogin = user.last_login
    create_time = datetime.datetime.now()
    username = user.username
    sqltype=sqltext.split()[0].lower()
    #获取ip地址
    ipaddr = get_client_ip(request)
    log = Oper_log (user=username,sqltext=sqltext,sqltype=sqltype,login_time=lastlogin,create_time=create_time,dbname=mydbname,dbtag=dbtag,ipaddr=ipaddr)
    log.save()
    return 1

def log_userlogin(request):
    username = request.user.username
    user = User.objects.get(username=username)
    ipaddr = get_client_ip(request)
    action = 'login'
    create_time = datetime.datetime.now()
    log = Login_log(user=username,ipaddr=ipaddr,action=action,create_time=create_time)
    log.save()

def log_loginfailed(request,username):

    ipaddr = get_client_ip(request)
    action = 'login_failed'
    create_time = datetime.datetime.now()
    log = Login_log(user=username, ipaddr=ipaddr, action=action,create_time=create_time)
    log.save()

def get_log_data(dbtag,optype,begin,end):
    if (optype=='all'):
        #如果结束时间小于开始时间，则以结束时间为准
        if (end > begin):
            log = Oper_log.objects.filter(dbtag=dbtag).filter(create_time__lte=end).filter(create_time__gte=begin).order_by("-create_time")[0:100]
        else:
            log = Oper_log.objects.filter(dbtag=dbtag).filter(create_time__lte=end).order_by("-create_time")[0:100]
    else:
        if (end > begin):
            log = Oper_log.objects.filter(dbtag=dbtag).filter(sqltype=optype).filter(create_time__lte=end).filter(create_time__gte=begin).order_by("-create_time")[0:100]
        else:
            log = Oper_log.objects.filter(dbtag=dbtag).filter(sqltype=optype).filter(create_time__lte=end).order_by("-create_time")[0:100]
    return log


def check_explain (sqltext):
    sqltext = sqltext.strip()
    sqltype = sqltext.split()[0].lower()
    if (sqltype =='select'):
        sqltext = 'explain extended '+sqltext
        return sqltext
    else:
        return wrong_msg

def my_key(group, request):
    try:
        real_ip = request.META['HTTP_X_FORWARDED_FOR']
        regip = real_ip.split(",")[0]
    except:
        try:
            regip = request.META['REMOTE_ADDR']
        except:
            regip = ""
    form = LoginForm(request.POST)
    myform = Captcha(request.POST)
    #验证码正确情况下，错误密码登录次数
    if form.is_valid() and myform.is_valid():
        username = form.cleaned_data['username']
        # password = form.cleaned_data['password']

        return regip+username
    #验证码错误不计算
    else:
        return regip+str(uuid.uuid1())


def get_client_ip(request):
    try:
        real_ip = request.META['HTTP_X_FORWARDED_FOR']
        regip = real_ip.split(",")[0]
    except:
        try:
            regip = request.META['REMOTE_ADDR']
        except:
            regip = ""
    return regip

def check_mysql_exec(sqltext,request,type='dml'):
    # request.user.has_perm('myapp.')
    sqltext = sqltext.strip()
    sqltype = sqltext.split()[0].lower()
    list_type = ['insert','update','delete','create','alter','drop','truncate','replace']
    if (sqltype=='insert'):
        if request.user.has_perm('myapp.can_insert_mysql'):
            return sqltext
        else:
            return "select 'Don\\'t have permission to \"insert\"'"
    elif(sqltype=='update' or sqltype == 'replace'):
        if request.user.has_perm('myapp.can_update_mysql'):
            return sqltext
        else:
            return "select 'Don\\'t have permission to \"update\"'"
    elif(sqltype=='delete'):
        if request.user.has_perm('myapp.can_delete_mysql'):
            return sqltext
        else:
            return "select 'Don\\'t have permission to \"delete\"'"
    elif(sqltype=='truncate'):
        if request.user.has_perm('myapp.can_truncate_mysql'):
            return sqltext
        else:
            return "select 'Don\\'t have permission to \"truncate\"'"
    elif(sqltype=='create'):
        if request.user.has_perm('myapp.can_create_mysql'):
            return sqltext
        else:
            return "select 'Don\\'t have permission to \"create\"'"
    elif(sqltype=='drop'):
        if request.user.has_perm('myapp.can_drop_mysql'):
            return sqltext
        else:
            return "select 'Don\\'t have permission to \"drop\"'"
    elif (sqltype == 'alter'):
        if request.user.has_perm('myapp.can_alter_mysql'):
            return sqltext
        else:
            return "select 'Don\\'t have permission to \"alter\"'"
    else:
        return wrong_msg

def run_mysql_exec(hosttag,sql,useraccount,request):
    #确认dbname
    a = Db_name.objects.filter(dbtag=hosttag)[0]
    #a = Db_name.objects.get(dbtag=hosttag)
    tar_dbname = a.dbname
    if (not cmp(sql,wrong_msg)):
        results,col = mysql_query(wrong_msg,user,passwd,host,int(port),dbname)
        return results,col,tar_dbname
    #如果instance中有备库role='write'，则选择从主库读取
    try:
        if a.instance.all().filter(role='write')[0]:
            tar_host = a.instance.all().filter(role='write')[0].ip
            tar_port = a.instance.all().filter(role='write')[0].port
    #如果没有设置或没有role=write，则选择第一个role=all的库读取
    except Exception,e:
        try:
            tar_host = a.instance.all().filter(role='all')[0].ip
            tar_port = a.instance.all().filter(role='all')[0].port
        except Exception,e:
            #没有找到role为all或者write的实例配置
            wrongmsg = "select \"" +str(e).replace('"',"\"")+"\""
            results,col = mysql_query(wrongmsg,user,passwd,host,int(port),dbname)
            return results,col,tar_dbname
    #find the useraccount and passwd for the user
    for i in a.db_account_set.all():
        if i.role != 'read' and i.role != 'admin':
            #find the specified account for the user
            if i.account.all().filter(username=useraccount):
                tar_username = i.user
                tar_passwd = i.passwd
                break
    #not find specified account for the user ,specified the public account to the user
    if not vars().has_key('tar_username'):
        for i in a.db_account_set.all():
            if i.role != 'read' and i.role != 'admin':
                # find the specified account for the user
                if i.account.all().filter(username=public_user):
                    tar_username = i.user
                    tar_passwd = i.passwd
                    break
    try:
        #之前根据check_mysql_exec判断过权限，如果是select则说明没权限，不记录日志
        if (sql.split()[0]!='select'):
            log_mysql_op(useraccount,sql,tar_dbname,hosttag,request)
            results,col = mysql_exec(sql,tar_username,tar_passwd,tar_host,tar_port,tar_dbname)
        else:
            results,col = mysql_query(sql,user,passwd,host,int(port),dbname)
    except Exception, e:
        #防止库连不上,返回一个wrong_message
        results,col = ([str(e)],''),['error']
    return results,col,tar_dbname



def mysql_exec(sql,user=user,passwd=passwd,host=host,port=int(port),dbname=dbname):
    try:
        conn=MySQLdb.connect(host=host,user=user,passwd=passwd,port=int(port),connect_timeout=5,charset='utf8')
        conn.select_db(dbname)
        curs = conn.cursor()
        result=curs.execute(sql)
        conn.commit()
        curs.close()
        conn.close()
        return (['影响行数: '+str(result)],''),['success']
    except Exception,e:
        if str(e)=='(2014, "Commands out of sync; you can\'t run this command now")':
            return (['只能输入单条sql语句'],''),['error']
        else:
            return([str(e)],''),['error']


def get_pre(dbtag):
    db = Db_name.objects.get(dbtag=dbtag)
    ins = db.instance.all()
    acc = db.account.all()
    acc_list = Db_account.objects.filter(dbname=db)
    gp = db.db_group_set.all()
    return acc_list,ins,acc,gp

def get_user_pre(username,request):
    if len(username)<=30:
        try :
            info = "PRIVILEGES FOR " + username
            dblist = User.objects.get(username=username).db_name_set.all()
        except :
            info = "PLEASE CHECK YOUR INPUT"
            dblist = User.objects.get(username=request.user.username).db_name_set.all()
    else:
        info = "INPUT TOO LONG"
        dblist = User.objects.get(username=request.user.username).db_name_set.all()
    return dblist,info

#used in prequery.html
def get_groupdb(group):
    grouplist = Db_group.objects.filter(groupname=group)
    return grouplist

#used in prequery.html
def get_privileges(username):
    pri = User.objects.get(username=username).user_permissions.all()
    return pri

def get_UserAndGroup():
    user_list = User.objects.exclude(username=public_user).order_by('username')
    group_list = Db_group.objects.all().order_by('groupname')

    # for row in User.objects.all():
    #     user_list.append(row.username)
    return user_list,group_list

def get_user_grouppri(username):
    user = User.objects.get(username=username)
    a = user.db_group_set.all()
    b = user.groups.all()
    return  a,b

def clear_userpri(username):
    user = User.objects.get(username=username)
    for i in Db_name.objects.all():
        i.account.remove(user)
    for i in Db_group.objects.all():
        i.account.remove(user)
    user.user_permissions.clear()
    user.groups.clear()

def set_groupdb(username,li):
    user = User.objects.get(username=username)
    tag_list=[]
    for i in li:
        tmp_gp = Db_group.objects.get(id=i)
        try:
            tmp_gp.account.add(user)
        except Exception,e:
            pass

        for x in tmp_gp.dbname.all():
            tag_list.append(x.dbtag)
            try:
                x.account.add(user)
            except Exception,e:
                pass
    tag_list = list(set(tag_list))
    return tag_list

#create user in pre_set.html
def create_user(username,passwd):
    if len(username)>0 and len(passwd)>0:
        user = User.objects.create_user(username=username,password=passwd)
        user.save()
    return user
#delete user in pre_set.html
def delete_user(username):
    user = User.objects.get(username=username)
    user.delete()

#user dbtaglist and user to set user-db relation
def set_user_db(user,dblist):
    setdblist = Db_name.objects.filter(dbtag__in=dblist)
    for i in setdblist:
        try:
            i.account.add(user)
            i.save()
        except Exception,e:
            pass

# a = Permission.objects.filter(codename__istartswith='can')


def set_usergroup(user,group):
    # user.groups.clear()
    grouplist = Group.objects.filter(name__in=group)
    for i in grouplist:
        try:
            user.groups.add(i)
            user.save()
        except Exception,e:
            pass
    # for i in a:
    #     print i.codename

def get_usergp_list():
    # perlist = Permission.objects.filter(codename__istartswith='can')
    grouplist = Group.objects.all().order_by('name')
    return grouplist




def main():
    return 1
if __name__=='__main__':
    main()
