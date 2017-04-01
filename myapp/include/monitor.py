from celery import task
from django.template import loader
from myapp.models import MySQL_monitor
import MySQLdb
from myapp.include.encrypt import prpcrypt
from myapp.tasks import sendmail

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
    for i in monlist:
        # longlist = []
        py = prpcrypt()
        conn_info  = Connect(i.instance.ip,i.instance.port,i.account.user,py.decrypt(i.account.passwd))
        result,col = conn_info.query_mysql("select * from processlist where command !='Sleep' and DB not in ('information_schema','sys') and user not in ('system user','event_scheduler') and command!='Binlog Dump'")
        if i.check_longsql == 1:
            longsql_send = filter(lambda x:x[5]>i.longsql_time,result)
            # print longsql_send
            if len(longsql_send)>0:
                if i.longsql_autokill  == 1:
                    idlist = map(lambda x:'kill '+str(x[0])+';',longsql_send)
                    conn_info.kill_id(idlist)
                    sendmail_monitor.delay(i.tag + '-LongSql_AutoKilled', i.mail_to.split(';'), longsql_send)
                else:
                    sendmail_monitor.delay(i.tag+'-LongSql_List',i.mail_to.split(';'),longsql_send)
        if i.check_active == 1:
            if len(result)>i.active_threshold :
                sendmail_monitor.delay(i.tag + '-ActiveSql_List', i.mail_to.split(';'), result)
