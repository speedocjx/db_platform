#!/bin/env python
#-*-coding:utf-8-*-
import pymysql, sys, datetime, commands, os
from myapp.include.encrypt import prpcrypt
from django.contrib.auth.models import User, Group
from myapp.models import Db_name, Db_account, Oper_log, Login_log, Db_group
from myapp.etc import config
from mypro import settings


reload(sys)
sys.setdefaultencoding('utf8')
import ConfigParser

host = settings.DATABASES['default']['HOST']
port = settings.DATABASES['default']['PORT']
user = settings.DATABASES['default']['USER']
passwd = settings.DATABASES['default']['PASSWORD']
dbname = settings.DATABASES['default']['NAME']
select_limit = int(config.select_limit)
export_limit = int(config.export_limit)
wrong_msg = config.wrong_msg
public_user = config.public_user
sqladvisor = config.sqladvisor
advisor_switch = config.sqladvisor_switch
path_mysqldiff = config.path_to_mysqldiff


def mysql_query(sql, user=user, passwd=passwd, host=host, port=int(port), dbname=dbname, limitnum=select_limit):
    try:
        conn = pymysql.connect(host=host, user=user, passwd=passwd, port=int(port), connect_timeout=5, charset='utf8')
        conn.select_db(dbname)
        cursor = conn.cursor()
        count = cursor.execute(sql)
        index = cursor.description
        col=[]
        #get column name
        for i in index:
            col.append(i[0])
        #result=cursor.fetchall()
        result = cursor.fetchmany(size=int(limitnum))
        cursor.close()
        conn.close()
        return (result,col)
    except Exception as e:
        return([str(e)],''),['error']


#获取下拉菜单列表
def get_mysql_hostlist(username, tag='tag', search=''):
    dbtype = 'mysql'
    host_list = []
    if len(search) == 0:
        if tag == 'tag':
            a = User.objects.get(username=username)
            #如果没有对应role='read'或者role='all'的account账号，则不显示在下拉菜单中
            for row in a.db_name_set.filter(db_account__role__in=['read','all']).filter(
                    instance__role__in=['read','all']).filter(instance__db_type=dbtype).values(
                    'dbtag').distinct().order_by("dbtag"):
                host_list.append(row['dbtag'])
        elif tag == 'log':
            for row in Db_name.objects.values('dbtag').distinct().order_by("dbtag"):
                host_list.append(row['dbtag'])
        elif tag == 'exec':
            a = User.objects.get(username=username)

            for row in a.db_name_set.filter(db_account__role__in=['write', 'all']).filter(
                    instance__role__in=['write', 'all']).filter(instance__db_type=dbtype).values(
                    'dbtag').all().distinct().order_by("dbtag"):
                host_list.append(row['dbtag'])
        elif tag == 'incept':
            a = User.objects.get(username=username)
            for row in a.db_name_set.filter(db_account__role='admin').filter(
                    instance__role__in=['write', 'all']).filter(instance__db_type=dbtype).values(
                    'dbtag').all().distinct().order_by("dbtag"):
                host_list.append(row['dbtag'])
        elif tag == 'meta':
            for row in Db_name.objects.filter(db_account__role='admin').filter(
                    instance__role__in=['write', 'all','read']).filter(instance__db_type=dbtype).values(
                    'dbtag').all().distinct().order_by("dbtag"):
                host_list.append(row['dbtag'])
    elif len(search) > 0:
        if tag == 'tag':
            a = User.objects.get(username=username)
            #如果没有对应role='read'或者role='all'的account账号，则不显示在下拉菜单中
            for row in a.db_name_set.filter(dbname__contains=search).filter(db_account__role__in=['read', 'all']).filter(
                    instance__role__in=['read', 'all']).filter(instance__db_type=dbtype).values(
                    'dbtag').distinct().order_by("dbtag"):
                host_list.append(row['dbtag'])
        elif tag == 'log':
            for row in Db_name.objects.values('dbtag').distinct().order_by("dbtag"):
                host_list.append(row['dbtag'])
        elif tag == 'exec':
            a = User.objects.get(username=username)
            #如果没有对应role='write'或者role='all'的account账号，则不显示在下拉菜单中
            # for row in a.db_name_set.filter(dbname__contains=search).order_by("dbtag"):
            #     if row.db_account_set.all().filter(role__in=['write','all']):
            # #排除只读实例
            #         if row.instance.all().filter(role__in=['write','all']).filter(db_type=dbtype):
            #             host_list.append(row.dbtag)
            for row in a.db_name_set.filter(dbname__contains=search).filter(db_account__role__in=['write', 'all']).filter(
                    instance__role__in=['write', 'all']).filter(instance__db_type=dbtype).values(
                    'dbtag').all().distinct().order_by("dbtag"):
                host_list.append(row['dbtag'])
        elif tag == 'incept':
            a = User.objects.get(username=username)
            for row in a.db_name_set.filter(dbname__contains=search).filter(db_account__role='admin').filter(
                    instance__role__in=['write', 'all']).filter(instance__db_type=dbtype).values(
                    'dbtag').all().distinct().order_by("dbtag"):
                host_list.append(row['dbtag'])
        elif tag == 'meta':
            for row in Db_name.objects.filter(dbname__contains=search).filter(db_account__role='admin').filter(
                    instance__role__in=['write', 'all','read']).filter(instance__db_type=dbtype).values(
                    'dbtag').all().distinct().order_by("dbtag"):
                host_list.append(row['dbtag'])
    return host_list


def get_op_type(methods='get'):
    #all表示所有种类
    op_list = ['all', 'incept', 'truncate', 'drop', 'create', 'delete', 'update', 'replace', 'insert', 'select',
             'explain', 'alter', 'rename', 'show']
    if methods == 'get':
        return op_list


def get_connection_info(hosttag, request):
    # 确认dbname
    a = Db_name.objects.filter(dbtag=hosttag)[0]
    # a = Db_name.objects.get(dbtag=hosttag)
    tar_dbname = a.dbname
    # 如果instance中有备库role='read'，则选择从备库读取
    try:
        if a.instance.all().filter(role='read')[0]:
            tar_host = a.instance.all().filter(role='read')[0].ip
            tar_port = a.instance.all().filter(role='read')[0].port
    # 如果没有设置或没有role=read，则选择第一个读到的all实例读取
    except Exception as e:
        tar_host = a.instance.filter(role='all')[0].ip
        tar_port = a.instance.filter(role='all')[0].port
        # tar_host = a.instance.all()[0].ip
        # tar_port = a.instance.all()[0].port
    pc = prpcrypt()
    for i in a.db_account_set.all():
        if i.role != 'write' and i.role != 'admin':
            # find the specified account for the user
            if i.account.all().filter(username=request.user.username):
                tar_username = i.user
                tar_passwd = pc.decrypt(i.passwd)
                break
    # not find specified account for the user ,specified the public account to the user

    if not vars().has_key('tar_username'):
        for i in a.db_account_set.all():
            if i.role != 'write' and i.role != 'admin':
                # find the specified account for the user
                if i.account.all().filter(username=public_user):
                    tar_username = i.user
                    tar_passwd = pc.decrypt(i.passwd)
                    break
    return tar_port, tar_passwd, tar_username, tar_host, tar_dbname


def get_advice(hosttag, sql, request):
    if advisor_switch != 0:
        tar_port, tar_passwd, tar_username, tar_host, tar_dbname = get_connection_info(hosttag,request)
        # print tar_port+tar_passwd+tar_username+tar_host
        sql=sql.replace('"','\\"').replace('`', '\`')[:-1]
        cmd = sqladvisor + ' -u %s -p %s -P %d -h %s -d %s -v 1 -q "%s"' % \
                           (tar_username, tar_passwd, int(tar_port), tar_host, tar_dbname, sql)
        # print cmd
        status, result_tmp = commands.getstatusoutput(cmd)
        # print result_tmp
        result_list = result_tmp.split('\n')
        results = ''
        for i in result_list:
            try:
                unicode(i, 'utf-8')
                results = results+'\n'+i
            except Exception as e:
                pass

        # results = results.replace('\xc0',' ').replace('\xbf',' ')
        print results
    else:
        results = 'sqladvisor not configured yet.'
    return results


def get_mysql_data(hosttag,sql, useraccount, request, limitnum):
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
    except Exception as e:
        tar_host = a.instance.filter(role='all')[0].ip
        tar_port = a.instance.filter(role='all')[0].port
        # tar_host = a.instance.all()[0].ip
        # tar_port = a.instance.all()[0].port
    pc = prpcrypt()
    for i in a.db_account_set.all():
        if i.role!='write' and i.role!='admin':
            # find the specified account for the user
            if i.account.all().filter(username=useraccount):
                tar_username = i.user
                tar_passwd = pc.decrypt(i.passwd)
                break
    #not find specified account for the user ,specified the public account to the user
    if not vars().has_key('tar_username'):
        for i in a.db_account_set.all():
            if i.role != 'write' and i.role != 'admin':
                # find the specified account for the user
                if i.account.all().filter(username=public_user):
                    tar_username = i.user
                    tar_passwd = pc.decrypt(i.passwd)
                    break
    #print tar_port+tar_passwd+tar_username+tar_host
    try:
        if cmp(sql,wrong_msg):
            log_mysql_op(useraccount, sql, tar_dbname, hosttag, request)
        results,col = mysql_query(sql, tar_username, tar_passwd, tar_host, tar_port, tar_dbname, limitnum)
    except Exception as e:
        #防止日志库记录失败，返回一个wrong_message
        results, col = ([str(e)], ''), ['error']
        #results,col = mysql_query(wrong_msg,user,passwd,host,int(port),dbname)
    return results, col, tar_dbname


#检查输入语句,并返回行限制数
def check_mysql_query(sqltext, user, type='select'):
    #根据user确定能够select或者export 的行数
    if type == 'export':
        try :
            num = User.objects.get(username=user).user_profile.export_limit
        except Exception as e:
            num = export_limit
    elif type == 'select':
        try:
            num = User.objects.get(username=user).user_profile.select_limit
        except Exception as e:
            num = select_limit
    num=str(num)
    limit = ' limit ' + num

    sqltext = sqltext.strip()
    sqltype = sqltext.split()[0].lower()
    list_type = ['select','show', 'desc', 'explain', 'describe']
    #flag 1位有效 0为list_type中的无效值
    flag = 0
    while True:
        sqltext = sqltext.strip()
        lastletter = sqltext[len(sqltext)-1]
        if not cmp(lastletter,';'):
            sqltext = sqltext[:-1]
        else:
            break
    #判断语句中是否已经存在limit，has_limit 为0时说明原来语句中是有limit的
    try:
        has_limit = cmp(sqltext.split()[-2].lower(), 'limit')
    except Exception as e:
        #prevent some input like '1' or 'ss' ...
        return wrong_msg, num

    for i in list_type:
        if not cmp(i, sqltype):
            flag = 1
            break
    if flag == 1:
        if sqltype == 'select' and has_limit != 0:
            return sqltext+limit,num
        elif sqltype == 'select' and has_limit == 0:
            if int(sqltext.split()[-1]) <= int(num):
                return sqltext, num
            else:
                tempsql = ''
                numlimit = sqltext.split()[-1]
                for i in sqltext.split()[0:-1]:
                    tempsql = tempsql+i+' '
                return tempsql + num,num
        else:
            return sqltext, num
    else:
        return wrong_msg, num


#记录用户所有操作
def log_mysql_op(user, sqltext, mydbname, dbtag, request):
    user = User.objects.get(username=user)
    #lastlogin = user.last_login+datetime.timedelta(hours=8)
    #create_time = datetime.datetime.now()+datetime.timedelta(hours=8)
    lastlogin = user.last_login
    create_time = datetime.datetime.now()
    username = user.username
    sqltype = sqltext.split()[0].lower()
    if sqltype in ['desc','describe']:
        sqltype = 'show'
    #获取ip地址
    ipaddr = get_client_ip(request)
    log = Oper_log(user=username, sqltext=sqltext, sqltype=sqltype, login_time=lastlogin,
                   create_time=create_time, dbname=mydbname, dbtag=dbtag, ipaddr=ipaddr)
    log.save()
    return 1


def log_mongo_op(sqltext, dbtag, tbname, request):
    user = User.objects.get(username=request.user.username)
    lastlogin = user.last_login
    create_time = datetime.datetime.now()
    username = user.username
    sqltype = 'select'
    ipaddr = get_client_ip(request)
    log = Oper_log(user=username, sqltext=sqltext, sqltype=sqltype, login_time=lastlogin,
                   create_time=create_time, dbname=tbname, dbtag=dbtag, ipaddr=ipaddr)
    log.save()
    return 1


def log_userlogin(request):
    username = request.user.username
    user = User.objects.get(username=username)
    ipaddr = get_client_ip(request)
    action = 'login'
    create_time = datetime.datetime.now()
    log = Login_log(user=username, ipaddr=ipaddr, action=action, create_time=create_time)
    log.save()


def log_loginfailed(request, username):
    ipaddr = get_client_ip(request)
    action = 'login_failed'
    create_time = datetime.datetime.now()
    log = Login_log(user=username, ipaddr=ipaddr, action=action, create_time=create_time)
    log.save()


def get_log_data(dbtag, optype, begin, end):
    if optype == 'all':
        # 如果结束时间小于开始时间，则以结束时间为准
        if end > begin:
            log = Oper_log.objects.filter(dbtag=dbtag).filter(
                create_time__lte=end).filter(create_time__gte=begin).order_by("-create_time")[0:100]
        else:
            log = Oper_log.objects.filter(dbtag=dbtag).filter(
                create_time__lte=end).order_by("-create_time")[0:100]
    else:
        if end > begin:
            log = Oper_log.objects.filter(dbtag=dbtag).filter(sqltype=optype).filter(
                create_time__lte=end).filter(create_time__gte=begin).order_by("-create_time")[0:100]
        else:
            log = Oper_log.objects.filter(dbtag=dbtag).filter(sqltype=optype).filter(
                create_time__lte=end).order_by("-create_time")[0:100]
    return log


def check_explain (sqltext):
    sqltext = sqltext.strip()
    sqltype = sqltext.split()[0].lower()
    if sqltype == 'select':
        sqltext = 'explain extended '+sqltext
        return sqltext
    else:
        return wrong_msg


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


def check_mysql_exec(sqltext, request, type='dml'):
    # request.user.has_perm('myapp.')
    sqltext = sqltext.strip()
    sqltype = sqltext.split()[0].lower()
    list_type = ['insert', 'update', 'delete', 'create', 'alter', 'rename', 'drop', 'truncate', 'replace']
    if sqltype == 'insert':
        if request.user.has_perm('myapp.can_insert_mysql'):
            return sqltext
        else:
            return "select 'Don\\'t have permission to \"insert\"'"
    elif sqltype == 'update' or sqltype == 'replace':
        if request.user.has_perm('myapp.can_update_mysql'):
            return sqltext
        else:
            return "select 'Don\\'t have permission to \"update\"'"
    elif sqltype == 'delete':
        if request.user.has_perm('myapp.can_delete_mysql'):
            return sqltext
        else:
            return "select 'Don\\'t have permission to \"delete\"'"
    elif sqltype == 'truncate':
        if request.user.has_perm('myapp.can_truncate_mysql'):
            return sqltext
        else:
            return "select 'Don\\'t have permission to \"truncate\"'"
    elif sqltype =='create':
        if request.user.has_perm('myapp.can_create_mysql'):
            return sqltext
        else:
            return "select 'Don\\'t have permission to \"create\"'"
    elif sqltype =='drop':
        if request.user.has_perm('myapp.can_drop_mysql'):
            return sqltext
        else:
            return "select 'Don\\'t have permission to \"drop\"'"
    elif sqltype == 'alter' or sqltype == 'rename':
        if request.user.has_perm('myapp.can_alter_mysql'):
            return sqltext
        else:
            return "select 'Don\\'t have permission to \"alter\"'"
    else:
        return wrong_msg


def run_mysql_exec(hosttag, sql, useraccount, request):
    #确认dbname
    a = Db_name.objects.filter(dbtag=hosttag)[0]
    #a = Db_name.objects.get(dbtag=hosttag)
    tar_dbname = a.dbname
    if not cmp(sql, wrong_msg):
        results,col = mysql_query(wrong_msg, user, passwd, host, int(port), dbname)
        return results,col,tar_dbname
    #如果instance中有备库role='write'，则选择从主库读取
    try:
        if a.instance.all().filter(role='write')[0]:
            tar_host = a.instance.all().filter(role='write')[0].ip
            tar_port = a.instance.all().filter(role='write')[0].port
    #如果没有设置或没有role=write，则选择第一个role=all的库读取
    except Exception as e:
        try:
            tar_host = a.instance.all().filter(role='all')[0].ip
            tar_port = a.instance.all().filter(role='all')[0].port
        except Exception as e:
            #没有找到role为all或者write的实例配置
            wrongmsg = "select \"" + str(e).replace('"', "\"")+"\""
            results,col = mysql_query(wrongmsg, user, passwd, host, int(port), dbname)
            return results, col, tar_dbname
    pc = prpcrypt()
    #find the useraccount and passwd for the user
    for i in a.db_account_set.all():
        if i.role != 'read' and i.role != 'admin':
            #find the specified account for the user
            if i.account.all().filter(username=useraccount):
                tar_username = i.user
                tar_passwd = pc.decrypt(i.passwd)
                break
    #not find specified account for the user ,specified the public account to the user
    if not vars().has_key('tar_username'):
        for i in a.db_account_set.all():
            if i.role != 'read' and i.role != 'admin':
                # find the specified account for the user
                if i.account.all().filter(username=public_user):
                    tar_username = i.user
                    tar_passwd = pc.decrypt(i.passwd)
                    break
    try:
        #之前根据check_mysql_exec判断过权限，如果是select则说明没权限，不记录日志
        if sql.split()[0] != 'select':
            log_mysql_op(useraccount, sql, tar_dbname, hosttag, request)
            results, col = mysql_exec(sql, tar_username, tar_passwd, tar_host, tar_port, tar_dbname)
        else:
            results, col = mysql_query(sql, user, passwd, host, int(port), dbname)
    except Exception as e:
        #防止库连不上,返回一个wrong_message
        results,col = ([str(e)], ''), ['error']
    return results, col, tar_dbname


def mysql_exec(sql, user=user, passwd=passwd, host=host, port=int(port), dbname=dbname):
    try:
        conn = pymysql.connect(host=host, user=user, passwd=passwd, port=int(port), connect_timeout=5, charset='utf8')
        conn.select_db(dbname)
        curs = conn.cursor()
        result = curs.execute(sql)
        conn.commit()
        curs.close()
        conn.close()
        return (['影响行数: '+str(result)],''), ['success']
    except Exception as e:
        if str(e) == '(2014, "Commands out of sync; you can\'t run this command now")':
            return (['只能输入单条sql语句'],''),['error']
        else:
            return([str(e)], ''), ['error']


def get_pre(dbtag):
    db = Db_name.objects.get(dbtag=dbtag)
    ins = db.instance.all()
    acc = db.account.all()
    acc_list = Db_account.objects.filter(dbname=db)
    gp = db.db_group_set.all()
    return acc_list, ins, acc, gp


def get_user_pre(username, request):
    if len(username) <= 30:
        try:
            info = "PRIVILEGES FOR " + username
            dblist = User.objects.get(username=username).db_name_set.all()
        except:
            info = "PLEASE CHECK YOUR INPUT"
            dblist = User.objects.get(username=request.user.username).db_name_set.all()
    else:
        info = "INPUT TOO LONG"
        dblist = User.objects.get(username=request.user.username).db_name_set.all()
    return dblist, info


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
    return user_list,group_list


def get_user_grouppri(username):
    user = User.objects.get(username=username)
    a = user.db_group_set.all()
    b = user.groups.all()
    return a,b


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
    tag_list = []
    for i in li:
        tmp_gp = Db_group.objects.get(id=i)
        try:
            tmp_gp.account.add(user)
        except:
            pass

        for x in tmp_gp.dbname.all():
            tag_list.append(x.dbtag)
            try:
                x.account.add(user)
            except:
                pass
    tag_list = list(set(tag_list))
    return tag_list


#create user in pre_set.html
def create_user(username, passwd, mail):
    if len(username) > 0 and len(passwd) > 0 and len(mail) > 0:
        user = User.objects.create_user(username=username, password=passwd, email=mail)
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
        except:
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


def get_diff(dbtag1, tb1, dbtag2, tb2):
    if os.path.isfile(path_mysqldiff):
        tar_host1, tar_port1, tar_username1, tar_passwd1,tar_dbname1 = get_conn_info(dbtag1)
        tar_host2, tar_port2, tar_username2, tar_passwd2,tar_dbname2 = get_conn_info(dbtag2)

        server1 = ' -q --server1={}:{}@{}:{}'.format(tar_username1,tar_passwd1,tar_host1,str(tar_port1))
        server2 = ' --server2={}:{}@{}:{}'.format(tar_username2,tar_passwd2,tar_host2,str(tar_port2))
        option = ' --difftype=sql'
        table = ' {}.{}:{}.{}'.format(tar_dbname1,tb1,tar_dbname2,tb2)
        cmd = path_mysqldiff + server1 + server2 + option + table
        output = os.popen(cmd)
        result = output.read()
        # result = commands.getoutput(cmd)
    else:
        result = "mysqldiff not installed"

    return result


def get_conn_info(hosttag):
    a = Db_name.objects.filter(dbtag=hosttag)[0]
    tar_dbname = a.dbname
    #如果instance中有备库role='read'，则选择从备库读取
    try:
        if a.instance.all().filter(role='read')[0]:
            tar_host = a.instance.all().filter(role='read')[0].ip
            tar_port = a.instance.all().filter(role='read')[0].port
    #如果没有设置或没有role=read，则选择第一个读到的实例读取
    except:
        tar_host = a.instance.filter(role__in=['write', 'all'])[0].ip
        tar_port = a.instance.filter(role__in=['write', 'all'])[0].port
    pc = prpcrypt()
    for i in a.db_account_set.all():
        if i.role == 'admin':
            tar_username = i.user
            tar_passwd = pc.decrypt(i.passwd)
            break
    return tar_host, tar_port, tar_username, tar_passwd, tar_dbname

