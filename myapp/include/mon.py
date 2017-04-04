from celery import task
import billiard
from django.template import loader
from myapp.models import MySQL_monitor
import MySQLdb,datetime
from myapp.include.encrypt import prpcrypt
from myapp.tasks import sendmail
from monitor.models import Mysql_processlist

class Connect(object):
    def __init__(self,ip=None,port=None,user=None,passwd=None):
        self.ip = ip
        self.port = int(port)
        self.user = user
        self.passwd = passwd
    def query_mysql(self,sql):
        try:
            conn=MySQLdb.connect(host=self.ip,user=self.user,passwd=self.passwd,port=self.port,connect_timeout=5,charset='utf8')
            conn.select_db('information_schema')
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
            return([str(e)],''),['error']
    def kill_id(self,idlist):
        try:
            conn=MySQLdb.connect(host=self.ip,user=self.user,passwd=self.passwd,port=self.port,connect_timeout=5,charset='utf8')
            conn.select_db('information_schema')
            curs = conn.cursor()
            for i in idlist:
                try:
                    curs.execute(i)
                except Exception, e:
                    pass
            conn.commit()
            curs.close()
            conn.close()
            results = 'success'
        except Exception, e:
             results = 'error'
        return results

@task
def sendmail_monitor(title,mailto,data):
    mon_sqllist = data
    html_content = loader.render_to_string('include/mail_template.html', locals())
    sendmail(title, mailto, html_content)

@task
def mon_processlist():
    monlist = MySQL_monitor.objects.filter(monitor=1)
    # plist=[]
    if len(monlist)>0:
        for i in monlist:
            # check_mysql.apply_async((i,),queue='mysql_monitor',routing_key='monitor.mysql')
            check_mysql.delay(i)


@task
def check_mysql(db):
    # longlist = []
    py = prpcrypt()
    conn_info  = Connect(db.instance.ip,db.instance.port,db.account.user,py.decrypt(db.account.passwd))
    # result,col = conn_info.query_mysql("select ID,USER,HOST,DB,COMMAND,TIME,STATE,INFO from processlist where command !='Sleep' and DB not in ('information_schema','sys') and user not in ('system user','event_scheduler') and command!='Binlog Dump'")
    result,col = conn_info.query_mysql("select ID,USER,HOST,DB,COMMAND,TIME,STATE,INFO from processlist")
    if db.check_longsql == 1:
        longsql_send = filter(lambda x:x[5]>db.longsql_time,result)
        # print longsql_send
        if len(longsql_send)>0:
            if db.longsql_autokill  == 1:
                idlist = map(lambda x:'kill '+str(x[0])+';',longsql_send)
                conn_info.kill_id(idlist)
                sendmail_monitor.delay(db.tag + '-LongSql_AutoKilled', db.mail_to.split(';'), longsql_send)
            else:
                sendmail_monitor.delay(db.tag+'-LongSql_List',db.mail_to.split(';'),longsql_send)
    if db.check_active == 1:
        if len(result)>db.active_threshold :
            sendmail_monitor.delay(db.tag + '-ActiveSql_List', db.mail_to.split(';'), result)
    insertlist=[]
    # for i in result:
    #     insertlist.append(Mysql_processlist(conn_id=i[0],user=i[1],host=i[2],db=i[3],\
    #                                     command=i[4],time=i[5],state=i[6],info=i[7]))
    if len(result)>0:
        insertlist = map(lambda x:Mysql_processlist(db_ip=db.instance.ip,db_port=db.instance.port,\
                                                    conn_id=x[0],user=x[1],host=x[2],db=x[3],\
                                                    command=x[4],time=x[5],state=x[6],info=x[7]),result)
        # print insertlist
        Mysql_processlist.objects.bulk_create(insertlist)