import MySQLdb, sys, string, time, datetime
from myapp.models import Db_name, Db_account, Db_instance, Oper_log, Task, Incep_error_log
from myapp.include import inception as incept
from celery import task
from myapp.tasks import process_runtask


# reload(sys)
# sys.setdefaultencoding('utf8')
# import ConfigParser
# import logging
# logging.basicConfig(level=logging.INFO,
#                     format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
#                     datefmt='%a, %d %b %Y %H:%M:%S',
#                     filename='/tmp/logger1.log',
#                     filemode='w')
#
# def get_config(group,config_name):
#     config = ConfigParser.ConfigParser()
#     config.readfp(open('/root/PycharmProjects/mypro/myapp/etc/config.ini','r'))
#     config_value=config.get(group,config_name).strip(' ').strip('\'').strip('\"')
#     return config_value
#
# def filters(data):
#     return data.strip(' ').strip('\n').strip('\br')
#
# host = get_config('settings','host')
# port = get_config('settings','port')
# user = get_config('settings','user')
# passwd = get_config('settings','passwd')
# dbname = get_config('settings','dbname')
# select_limit = int(get_config('settings','select_limit'))
# export_limit = int(get_config('settings','export_limit'))
# wrong_msg = get_config('settings','wrong_msg')
# incp_host = get_config('settings','incp_host')
# incp_port = int(get_config('settings','incp_port'))
# incp_user = get_config('settings','incp_user')
# incp_passwd = get_config('settings','incp_passwd')
# public_user = get_config('settings','public_user')


host = incept.host
port = incept.port
user = incept.user
passwd = incept.passwd
dbname = incept.dbname
select_limit = incept.select_limit
export_limit = incept.export_limit
wrong_msg = incept.wrong_msg
incp_host = incept.incp_host
incp_port = incept.incp_port
incp_user = incept.incp_user
incp_passwd = incept.incp_passwd
public_user = incept.public_user

@task
def task_sche_run():
    try:
        print "starting scheduler task"
        task = Task.objects.filter(status='appointed').filter(sche_time__lte=datetime.datetime.now())
        if len(task)>0:
            for mytask in task:
                print "mytask_id"
                print mytask.id
                hosttag = mytask.dbtag
                status = 'running'
                sql = mytask.sqltext
                mycreatetime = mytask.create_time
                mytask.status = status
                mytask.update_time = datetime.datetime.now()
                mytask.save()
                log_incep_op(sql, hosttag, mycreatetime)
                process_runtask.delay(hosttag, sql, mytask)
                #Process(target=process_runtask, args=).start()
    except Exception,e:
        print e

def log_incep_op(sqltext,dbtag,mycreatetime):
    lastlogin = mycreatetime
    create_time = mycreatetime
    username = 'scheduled'
    sqltype='incept'
    ipaddr = 'localhost'
    log = Oper_log (user=username,sqltext=sqltext,sqltype=sqltype,login_time=lastlogin,create_time=create_time,dbname='',dbtag=dbtag,ipaddr=ipaddr)
    log.save()
    return 1

def incep_exec(sqltext,myuser,mypasswd,myhost,myport,mydbname,flag=0):
    if (int(flag)==0):
        flagcheck='--enable-check'
    elif(int(flag)==1):
        flagcheck='--enable-execute'
    myuser=myuser.encode('utf8')
    mypasswd = mypasswd.encode('utf8')
    myhost=myhost.encode('utf8')
    myport=int(myport)
    mydbname=mydbname.encode('utf8')
    sql1="/*--user=%s;--password=%s;--host=%s;%s;--port=%d;*/\
            inception_magic_start;\
            use %s;"% (myuser,mypasswd,myhost,flagcheck,myport,mydbname)
    sql2='inception_magic_commit;'
    sql = sql1 + sqltext + sql2
    try:
        conn=MySQLdb.connect(host=incp_host,user=incp_user,passwd=incp_passwd,db='',port=incp_port,use_unicode=True, charset="utf8")
        cur=conn.cursor()
        ret=cur.execute(sql)
        result=cur.fetchall()
        #num_fields = len(cur.description)
        field_names = [i[0] for i in cur.description]
        cur.close()
        conn.close()
    except MySQLdb.Error,e:
        return([str(e)],''),['error']
    return result,field_names
    #return result[1][4].split("\n")

#flag=0 for check and 1 for execute
def inception_check(hosttag,sql,flag=0):
    # make_sure_mysql_usable()
    a = Db_name.objects.get(dbtag=hosttag)
    #a = Db_name.objects.get(dbtag=hosttag)
    tar_dbname = a.dbname
    if (not cmp(sql,wrong_msg)):
        results,col = mysql_query(wrong_msg,user,passwd,host,int(port),dbname)
        return results,col,tar_dbname
    try:
        if a.instance.all().filter(role='write')[0]:
            tar_host = a.instance.all().filter(role='write')[0].ip
            tar_port = a.instance.all().filter(role='write')[0].port
    except Exception,e:
        try:
            tar_host = a.instance.all().filter(role='all')[0].ip
            tar_port = a.instance.all().filter(role='all')[0].port
        except Exception,e:
            wrongmsg = "select \"" +str(e).replace('"',"\"")+"\""
            results,col = mysql_query(wrongmsg,user,passwd,host,int(port),dbname)
            return results,col,tar_dbname
    tag=0
    for i in a.db_account_set.all():
        if i.role=='admin':
            tar_username = i.user
            tar_passwd = i.passwd
            break
    #print tar_port+tar_passwd+tar_username+tar_host
    try:
        results,col = incep_exec(sql,tar_username,tar_passwd,tar_host,tar_port,tar_dbname,flag)
        return results,col,tar_dbname
    except Exception,e:
        wrongmsg = "select \"no admin account being setted\""
        results, col = mysql_query(wrongmsg, user, passwd, host, int(port), dbname)
        return results, col, tar_dbname


# def process_runtask(hosttag,sqltext,mytask):
#     results,col,tar_dbname = inception_check(hosttag,sqltext,1)
#     status='executed'
#     c_time = mytask.create_time
#     mytask.update_time = datetime.datetime.now()
#     # make_sure_mysql_usable()
#     mytask.save()
#     for row in results:
#         try:
#             inclog = Incep_error_log(myid=row[0],stage=row[1],errlevel=row[2],stagestatus=row[3],errormessage=row[4],\
#                          sqltext=row[5],affectrow=row[6],sequence=row[7],backup_db=row[8],execute_time=row[9],sqlsha=row[10],\
#                          create_time=c_time,finish_time=mytask.update_time)
#             # make_sure_mysql_usable()
#             inclog.save()
#         except Exception,e:
#             inclog = Incep_error_log(myid=999,stage='',errlevel=999,stagestatus='',errormessage=row[0],\
#                          sqltext=e,affectrow=999,sequence='',backup_db='',execute_time='',sqlsha='',\
#                          create_time=c_time,finish_time=mytask.update_time)
#             # make_sure_mysql_usable()
#             inclog.save()
#         if (int(row[2])!=0):
#             status='executed failed'
#             #record error message of incept exec
#     mytask.status = status
#     # make_sure_mysql_usable()
#     mytask.save()




# def make_sure_mysql_usable():
#     # mysql is lazily connected to in django.
#     # connection.connection is None means
#     # you have not connected to mysql before
#     if connection.connection and not connection.is_usable():
#         # destroy the default mysql connection
#         # after this line, when you use ORM methods
#         # django will reconnect to the default mysql
#         del connections._connections.default


def mysql_query(sql,user=user,passwd=passwd,host=host,port=int(port),dbname=dbname):
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
        result=cursor.fetchall()
        cursor.close()
        conn.close()
        return (result,col)
    except Exception,e:
        print e
        return([str(e)],''),['error']

@task
def table_check():
    #archive history data
    sql = "insert into mon_autoinc_status_his (TABLE_SCHEMA ,TABLE_NAME,COLUMN_NAME,DATA_TYPE,\
            COLUMN_TYPE,IS_UNSIGNED,IS_INT,MAX_VALUE,AUTO_INCREMENT,INDEX_NAME,\
            SEQ_IN_INDEX,DBTAG,update_time) select TABLE_SCHEMA ,TABLE_NAME,COLUMN_NAME,DATA_TYPE,\
            COLUMN_TYPE,IS_UNSIGNED,IS_INT,MAX_VALUE,AUTO_INCREMENT,INDEX_NAME,\
            SEQ_IN_INDEX,DBTAG,update_time from mon_autoinc_status"
    mysql_exec(sql)
    sql = "insert into mon_tbsize_his (TABLE_SCHEMA,TABLE_NAME,`DATA(M)`,\
            `INDEX(M)`,`TOTAL(M)`,DBTAG,update_time) select TABLE_SCHEMA,TABLE_NAME,`DATA(M)`,\
            `INDEX(M)`,`TOTAL(M)`,DBTAG,update_time from mon_tbsize"
    mysql_exec(sql)
    #clear tmp table
    mysql_exec("truncate table mon_autoinc_status_tmp")
    mysql_exec("truncate table mon_tbsize_tmp")
    print datetime.datetime.now()
    for i in Db_name.objects.filter(instance__db_type='mysql').all():
        try:
            print i.dbtag
            print "start collect auto_increment status"
            sql = "SELECT\
            TABLE_SCHEMA,\
            TABLE_NAME,\
            COLUMNS.COLUMN_NAME,\
            COLUMNS.DATA_TYPE,\
            COLUMNS.COLUMN_TYPE,\
            IF(LOCATE('unsigned', COLUMN_TYPE) > 0,\
            1,\
            0\
            ) AS IS_UNSIGNED,\
            IF(LOCATE('int', DATA_TYPE) > 0,\
            1,\
            0\
            ) AS IS_INT,\
            (CASE DATA_TYPE\
            WHEN 'tinyint' THEN 255\
            WHEN 'smallint' THEN 65535\
            WHEN 'mediumint' THEN 16777215\
            WHEN 'int' THEN 4294967295\
            WHEN 'bigint' THEN 18446744073709551615\
            END >> IF(LOCATE('unsigned', COLUMN_TYPE) > 0, 0, 1)\
            ) AS MAX_VALUE,\
            AUTO_INCREMENT,\
            INDEX_NAME,\
            SEQ_IN_INDEX,'" + i.dbtag + "'\
            FROM INFORMATION_SCHEMA.COLUMNS INNER JOIN INFORMATION_SCHEMA.TABLES USING (TABLE_SCHEMA, TABLE_NAME) INNER JOIN INFORMATION_SCHEMA.STATISTICS USING (TABLE_SCHEMA, TABLE_NAME, COLUMN_NAME)\
            WHERE SEQ_IN_INDEX=1 AND \
            EXTRA='auto_increment' AND TABLE_SCHEMA='" + i.dbname + "' GROUP BY TABLE_SCHEMA,\
            TABLE_NAME,COLUMN_NAME HAVING AUTO_INCREMENT/MAX_VALUE>=0;"
            param, col = get_data(i, sql)

            insertsql = "insert into mon_autoinc_status_tmp (TABLE_SCHEMA ,TABLE_NAME,COLUMN_NAME,DATA_TYPE,\
            COLUMN_TYPE,IS_UNSIGNED,IS_INT,MAX_VALUE,AUTO_INCREMENT,INDEX_NAME,\
            SEQ_IN_INDEX,DBTAG) values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"

            exec_many(insertsql, list(param))
            print "start connect tbsize info"
            sql = "SELECT TABLE_SCHEMA,TABLE_NAME,\
            ROUND(DATA_LENGTH/(1024*1024),2) 'DATA(M)',\
            ROUND(INDEX_LENGTH/(1024*1024),2) 'INDEX(M)',\
            ROUND(( DATA_LENGTH + INDEX_LENGTH )/( 1024 * 1024 ), 2) 'TOTAL(M)' \
            ,'" + i.dbtag + "' FROM  INFORMATION_SCHEMA.TABLES WHERE TABLE_SCHEMA='"+ i.dbname +"' "
            param, col = get_data(i, sql)
            # print param
            insertsql = "insert into mon_tbsize_tmp (TABLE_SCHEMA,TABLE_NAME,`DATA(M)`,\
            `INDEX(M)`,`TOTAL(M)`,DBTAG) values (%s,%s,%s,%s,%s,%s)"
            exec_many(insertsql, list(param))

        except Exception, e:
            print e
            pass
    mysql_exec("rename table mon_autoinc_status to mon_autoinc_status_tmp1,mon_autoinc_status_tmp to mon_autoinc_status")
    mysql_exec("rename table mon_autoinc_status_tmp1 to mon_autoinc_status_tmp")
    mysql_exec("rename table mon_tbsize_last to mon_tbsize_last1")
    mysql_exec("rename table mon_tbsize to mon_tbsize_last,mon_tbsize_tmp to mon_tbsize,mon_tbsize_last1 to mon_tbsize_tmp")
    #record dbsize
    mysql_exec("insert into mon_dbsize_his (DBTAG,`DATA(M)`,`INDEX(M)`,`TOTAL(M)`) select DBTAG,sum(`DATA(M)`),sum(`INDEX(M)`),sum(`TOTAL(M)`) from mon_tbsize group by DBTAG")
def get_data(a,sql):
    #a = Db_name.objects.get(dbtag=hosttag)
    tar_dbname = a.dbname
    try:
        if a.instance.all().filter(role='read')[0]:
            tar_host = a.instance.all().filter(role='read')[0].ip
            tar_port = a.instance.all().filter(role='read')[0].port
    except Exception,e:
        tar_host = a.instance.filter(role__in=['write','all'])[0].ip
        tar_port = a.instance.filter(role__in=['write','all'])[0].port
    for i in a.db_account_set.all():
        if i.role == 'admin':
            tar_username = i.user
            tar_passwd = i.passwd
            break
    #print tar_port+tar_passwd+tar_username+tar_host
    try:
        results,col = mysql_query(sql,tar_username,tar_passwd,tar_host,tar_port,tar_dbname)
    except Exception, e:
        #wrong_message
        results,col = ([str(e)],''),['error']
        #results,col = mysql_query(wrong_msg,user,passwd,host,int(port),dbname)
    return results,col

def exec_many(insertsql,param):
    try:
        conn = MySQLdb.connect(host=host, user=user, passwd=passwd, port=int(port), connect_timeout=5, charset='utf8')
        conn.select_db(dbname)
        cursor = conn.cursor()
        # cursor.execute("truncate table mon_autoinc_status")
        cursor.executemany(insertsql,param)
        conn.commit()
        cursor.close()
        conn.close()
    except Exception,e:
        print e

def mysql_exec(sql):
    try:
        conn = MySQLdb.connect(host=host, user=user, passwd=passwd, port=int(port), connect_timeout=5, charset='utf8')
        conn.select_db(dbname)
        cursor = conn.cursor()
        # cursor.execute("truncate table mon_autoinc_status")
        cursor.execute(sql)
        conn.commit()
        cursor.close()
        conn.close()
    except Exception,e:
        print e


