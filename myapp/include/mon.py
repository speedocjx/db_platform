from celery import task
import time,string
from django.template import loader
from myapp.models import MySQL_monitor
import MySQLdb,datetime
from myapp.include.encrypt import prpcrypt
from myapp.tasks import sendmail
from monitor.models import Mysql_processlist,Mysql_replication,MysqlStatus,Alarm,AlarmTemp
from myapp.include.scheduled import mysql_exec

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

# active sql,long sql,replication,connections
@task
def sendmail_monitor(title,mailto,data,alarm_type):
    if alarm_type in ['active sql','long sql']:
        mon_sqllist = data
    else:
        alarm_information = data
    html_content = loader.render_to_string('include/mail_template.html', locals())
    sendmail(title, mailto, html_content)

@task
def mon_mysql():
    monlist = MySQL_monitor.objects.filter(monitor=1)
    no_monlist = MySQL_monitor.objects.filter(monitor=0)


    if len(no_monlist)>0:
        for i in no_monlist:

            Mysql_replication.objects.filter(db_ip=i.instance.ip).filter(db_port=i.instance.port).delete()
            MysqlStatus.objects.filter(db_ip=i.instance.ip).filter(db_port=i.instance.port).delete()
    # plist=[]
    if len(monlist)>0:
        for i in monlist:

            # check_mysql.apply_async((i,),queue='mysql_monitor',routing_key='monitor.mysql')
            check_mysql_host.delay(i)


@task
def check_mysql_host(db):

    mon_basic(db)
    # longlist = []
    py = prpcrypt()
    conn_info  = Connect(db.instance.ip,db.instance.port,db.account.user,py.decrypt(db.account.passwd))
    result,col = conn_info.query_mysql("select ID,USER,HOST,DB,COMMAND,TIME,STATE,INFO from processlist where command !='Sleep' and DB not in ('information_schema','sys') and user not in ('system user','event_scheduler') and command!='Binlog Dump'")
    # result,col = conn_info.query_mysql("select ID,USER,HOST,DB,COMMAND,TIME,STATE,INFO from processlist")

    if db.check_longsql == 1:
        longsql_send = filter(lambda x:x[5]>db.longsql_time,result)
        # print longsql_send
        alarm_type = 'long sql'
        if len(longsql_send)>0:
            flag = record_alarm(db, alarm_type)
            if db.longsql_autokill  == 1:
                idlist = map(lambda x:'kill '+str(x[0])+';',longsql_send)
                conn_info.kill_id(idlist)
                if flag:
                    sendmail_monitor.delay(db.tag + '-LongSql_AutoKilled', db.mail_to.split(';'), longsql_send,alarm_type)
            else:
                sendmail_monitor.delay(db.tag+'-LongSql_List',db.mail_to.split(';'),longsql_send,alarm_type)
        else:
            check_ifok(db, alarm_type)
    if db.check_active == 1:
        alarm_type = 'active sql'
        if len(result)>db.active_threshold :
            if record_alarm(db, alarm_type):
                sendmail_monitor.delay(db.tag + '-ActiveSql_List', db.mail_to.split(';'), result,alarm_type)
        else:
            check_ifok(db, alarm_type)
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

def record_alarm(db,alarm_type):
    time = datetime.datetime.now()-datetime.timedelta(minutes=db.alarm_interval)
    if len(AlarmTemp.objects.filter(db_ip=db.instance.ip, db_port=db.instance.port,alarm_type=alarm_type,create_time__gte=time))<db.alarm_times:
        new_alarm = Alarm(send_mail=1,db_ip=db.instance.ip, db_port=db.instance.port, alarm_type=alarm_type)
        new_alarm.save()
        new_alarm1 = AlarmTemp(db_ip=db.instance.ip, db_port=db.instance.port, alarm_type=alarm_type)
        new_alarm1.save()
        return True
    else:
        new_alarm = Alarm(send_mail=0, db_ip=db.instance.ip, db_port=db.instance.port, alarm_type=alarm_type)
        new_alarm.save()
        return False

def check_ifok(db,alarm_type):
    if AlarmTemp.objects.filter(db_ip=db.instance.ip, db_port=db.instance.port,alarm_type=alarm_type):
        AlarmTemp.objects.filter(db_ip=db.instance.ip, db_port=db.instance.port, alarm_type=alarm_type).delete()
        sendmail_monitor.delay(db.tag, db.mail_to.split(';'), alarm_type+' ok', alarm_type)



def mon_basic(db):
    try:
        py = prpcrypt()
        conn = MySQLdb.connect(host=db.instance.ip, user=db.account.user, passwd=py.decrypt(db.account.passwd), port=int(db.instance.port), connect_timeout=3, charset='utf8')
        conn.autocommit(True)
        cur = conn.cursor()
        conn.select_db('information_schema')

        ############################# CHECK MYSQL ####################################################
        mysql_variables = get_mysql_variables(cur)
        mysql_status = get_mysql_status(cur)
        time.sleep(1)
        mysql_status_2 = get_mysql_status(cur)
        ############################# GET VARIABLES ###################################################
        version = get_item(mysql_variables, 'version')
        key_buffer_size = get_item(mysql_variables, 'key_buffer_size')
        sort_buffer_size = get_item(mysql_variables, 'sort_buffer_size')
        join_buffer_size = get_item(mysql_variables, 'join_buffer_size')
        max_connections = get_item(mysql_variables, 'max_connections')
        max_connect_errors = get_item(mysql_variables, 'max_connect_errors')
        open_files_limit = get_item(mysql_variables, 'open_files_limit')
        table_open_cache = get_item(mysql_variables, 'table_open_cache')
        max_tmp_tables = get_item(mysql_variables, 'max_tmp_tables')
        max_heap_table_size = get_item(mysql_variables, 'max_heap_table_size')
        max_allowed_packet = get_item(mysql_variables, 'max_allowed_packet')
        thread_cache_size = get_item(mysql_variables, 'thread_cache_size')
        ############################# GET INNODB INFO ##################################################
        # innodb variables
        innodb_version = get_item(mysql_variables, 'innodb_version')
        innodb_buffer_pool_instances = get_item(mysql_variables, 'innodb_buffer_pool_instances')
        innodb_buffer_pool_size = get_item(mysql_variables, 'innodb_buffer_pool_size')
        innodb_doublewrite = get_item(mysql_variables, 'innodb_doublewrite')
        innodb_file_per_table = get_item(mysql_variables, 'innodb_file_per_table')
        innodb_flush_log_at_trx_commit = get_item(mysql_variables, 'innodb_flush_log_at_trx_commit')
        innodb_flush_method = get_item(mysql_variables, 'innodb_flush_method')
        innodb_force_recovery = get_item(mysql_variables, 'innodb_force_recovery')
        innodb_io_capacity = get_item(mysql_variables, 'innodb_io_capacity')
        innodb_read_io_threads = get_item(mysql_variables, 'innodb_read_io_threads')
        innodb_write_io_threads = get_item(mysql_variables, 'innodb_write_io_threads')
        # innodb status
        innodb_buffer_pool_pages_total = int(get_item(mysql_status, 'Innodb_buffer_pool_pages_total'))
        innodb_buffer_pool_pages_data = int(get_item(mysql_status, 'Innodb_buffer_pool_pages_data'))
        innodb_buffer_pool_pages_dirty = int(get_item(mysql_status, 'Innodb_buffer_pool_pages_dirty'))
        innodb_buffer_pool_pages_flushed = int(get_item(mysql_status, 'Innodb_buffer_pool_pages_flushed'))
        innodb_buffer_pool_pages_free = int(get_item(mysql_status, 'Innodb_buffer_pool_pages_free'))
        innodb_buffer_pool_pages_misc = int(get_item(mysql_status, 'Innodb_buffer_pool_pages_misc'))
        innodb_buffer_pool_wait_free = int(get_item(mysql_status, 'Innodb_buffer_pool_wait_free'))
        if innodb_buffer_pool_pages_misc > 18046744073709540000:
            innodb_buffer_pool_pages_misc = 0
        innodb_page_size = int(get_item(mysql_status, 'Innodb_page_size'))
        innodb_pages_created = int(get_item(mysql_status, 'Innodb_pages_created'))
        innodb_pages_read = int(get_item(mysql_status, 'Innodb_pages_read'))
        innodb_pages_written = int(get_item(mysql_status, 'Innodb_pages_written'))
        innodb_row_lock_current_waits = int(get_item(mysql_status, 'Innodb_row_lock_current_waits'))
        innodb_row_lock_time = int(get_item(mysql_status, 'Innodb_row_lock_time'))
        innodb_row_lock_waits = int(get_item(mysql_status, 'Innodb_row_lock_waits'))
        innodb_log_waits = int(get_item(mysql_status, 'Innodb_log_waits'))
        # innodb persecond info
        innodb_buffer_pool_read_requests_persecond = int(
            get_item(mysql_status_2, 'Innodb_buffer_pool_read_requests')) - int(
            get_item(mysql_status, 'Innodb_buffer_pool_read_requests'))
        innodb_buffer_pool_reads_persecond = int(get_item(mysql_status_2, 'Innodb_buffer_pool_reads')) - int(
            get_item(mysql_status, 'Innodb_buffer_pool_reads'))
        innodb_buffer_pool_write_requests_persecond = int(
            get_item(mysql_status_2, 'Innodb_buffer_pool_write_requests')) - int(
            get_item(mysql_status, 'Innodb_buffer_pool_write_requests'))
        innodb_buffer_pool_pages_flushed_persecond = int(
            get_item(mysql_status_2, 'Innodb_buffer_pool_pages_flushed')) - int(
            get_item(mysql_status, 'Innodb_buffer_pool_pages_flushed'))
        innodb_rows_deleted_persecond = int(get_item(mysql_status_2, 'Innodb_rows_deleted')) - int(
            get_item(mysql_status, 'Innodb_rows_deleted'))
        innodb_rows_inserted_persecond = int(get_item(mysql_status_2, 'Innodb_rows_inserted')) - int(
            get_item(mysql_status, 'Innodb_rows_inserted'))
        innodb_rows_read_persecond = int(get_item(mysql_status_2, 'Innodb_rows_read')) - int(
            get_item(mysql_status, 'Innodb_rows_read'))
        innodb_rows_updated_persecond = int(get_item(mysql_status_2, 'Innodb_rows_updated')) - int(
            get_item(mysql_status, 'Innodb_rows_updated'))
        ############################# GET STATUS ##################################################
        connect = 1
        uptime = get_item(mysql_status, 'Uptime')
        open_files = get_item(mysql_status, 'Open_files')
        open_tables = get_item(mysql_status, 'Open_tables')
        opened_tables = get_item(mysql_status, 'Opened_tables')
        threads_connected = get_item(mysql_status, 'Threads_connected')
        threads_running = get_item(mysql_status, 'Threads_running')
        threads_created = get_item(mysql_status, 'Threads_created')
        threads_cached = get_item(mysql_status, 'Threads_cached')
        # threads_waits = 20
        max_used_connections = get_item(mysql_status, 'Max_used_connections')
        connections = get_item(mysql_status, 'Connections')
        aborted_clients = get_item(mysql_status, 'Aborted_clients')
        aborted_connects = get_item(mysql_status, 'Aborted_connects')
        key_blocks_not_flushed = get_item(mysql_status, 'Key_blocks_not_flushed')
        key_blocks_unused = get_item(mysql_status, 'Key_blocks_unused')
        key_blocks_used = get_item(mysql_status, 'Key_blocks_used')
        slow_queries = int(get_item(mysql_status, 'Slow_queries'))
        ############################# GET STATUS PERSECOND ##################################################


        threads_created_percond = int(get_item(mysql_status_2, 'Threads_created')) - int(threads_created)
        connections_persecond = int(get_item(mysql_status_2, 'Connections')) - int(get_item(mysql_status, 'Connections'))
        bytes_received_persecond = (int(get_item(mysql_status_2, 'Bytes_received')) - int(
            get_item(mysql_status, 'Bytes_received'))) / 1024
        bytes_sent_persecond = (int(get_item(mysql_status_2, 'Bytes_sent')) - int(
            get_item(mysql_status, 'Bytes_sent'))) / 1024
        com_select_persecond = int(get_item(mysql_status_2, 'Com_select')) - int(get_item(mysql_status, 'Com_select'))
        com_insert_persecond = int(get_item(mysql_status_2, 'Com_insert')) - int(get_item(mysql_status, 'Com_insert'))
        com_update_persecond = int(get_item(mysql_status_2, 'Com_update')) - int(get_item(mysql_status, 'Com_update'))
        com_delete_persecond = int(get_item(mysql_status_2, 'Com_delete')) - int(get_item(mysql_status, 'Com_delete'))
        com_commit_persecond = int(get_item(mysql_status_2, 'Com_commit')) - int(get_item(mysql_status, 'Com_commit'))
        com_rollback_persecond = int(get_item(mysql_status_2, 'Com_rollback')) - int(get_item(mysql_status, 'Com_rollback'))
        questions_persecond = int(get_item(mysql_status_2, 'Questions')) - int(get_item(mysql_status, 'Questions'))
        queries_persecond = int(get_item(mysql_status_2, 'Queries')) - int(get_item(mysql_status, 'Queries'))
        transaction_persecond = (int(get_item(mysql_status_2, 'Com_commit')) + int(
            get_item(mysql_status_2, 'Com_rollback'))) - (
                                int(get_item(mysql_status, 'Com_commit')) + int(get_item(mysql_status, 'Com_rollback')))
        created_tmp_disk_tables_persecond = int(get_item(mysql_status_2, 'Created_tmp_disk_tables')) - int(
            get_item(mysql_status, 'Created_tmp_disk_tables'))
        created_tmp_files_persecond = int(get_item(mysql_status_2, 'Created_tmp_files')) - int(
            get_item(mysql_status, 'Created_tmp_files'))
        created_tmp_tables_persecond = int(get_item(mysql_status_2, 'Created_tmp_tables')) - int(
            get_item(mysql_status, 'Created_tmp_tables'))
        table_locks_immediate_persecond = int(get_item(mysql_status_2, 'Table_locks_immediate')) - int(
            get_item(mysql_status, 'Table_locks_immediate'))
        table_locks_waited_persecond = int(get_item(mysql_status_2, 'Table_locks_waited')) - int(
            get_item(mysql_status, 'Table_locks_waited'))
        key_read_requests_persecond = int(get_item(mysql_status_2, 'Key_read_requests')) - int(
            get_item(mysql_status, 'Key_read_requests'))
        key_reads_persecond = int(get_item(mysql_status_2, 'Key_reads')) - int(get_item(mysql_status, 'Key_reads'))
        key_write_requests_persecond = int(get_item(mysql_status_2, 'Key_write_requests')) - int(
            get_item(mysql_status, 'Key_write_requests'))
        key_writes_persecond = int(get_item(mysql_status_2, 'Key_writes')) - int(get_item(mysql_status, 'Key_writes'))
        ############################# GET MYSQL HITRATE ##################################################
        if (string.atof(get_item(mysql_status, 'Qcache_hits')) + string.atof(get_item(mysql_status, 'Com_select'))) <> 0:
            query_cache_hitrate = string.atof(get_item(mysql_status, 'Qcache_hits')) / (
            string.atof(get_item(mysql_status, 'Qcache_hits')) + string.atof(get_item(mysql_status, 'Com_select')))
            query_cache_hitrate = "%9.2f" % query_cache_hitrate
        else:
            query_cache_hitrate = 0

        if string.atof(get_item(mysql_status, 'Connections')) <> 0:
            thread_cache_hitrate = 1 - string.atof(get_item(mysql_status, 'Threads_created')) / string.atof(
                get_item(mysql_status, 'Connections'))
            thread_cache_hitrate = "%9.2f" % thread_cache_hitrate
        else:
            thread_cache_hitrate = 0

        if string.atof(get_item(mysql_status, 'Key_read_requests')) <> 0:
            key_buffer_read_rate = 1 - string.atof(get_item(mysql_status, 'Key_reads')) / string.atof(
                get_item(mysql_status, 'Key_read_requests'))
            key_buffer_read_rate = "%9.2f" % key_buffer_read_rate
        else:
            key_buffer_read_rate = 0

        if string.atof(get_item(mysql_status, 'Key_write_requests')) <> 0:
            key_buffer_write_rate = 1 - string.atof(get_item(mysql_status, 'Key_writes')) / string.atof(
                get_item(mysql_status, 'Key_write_requests'))
            key_buffer_write_rate = "%9.2f" % key_buffer_write_rate
        else:
            key_buffer_write_rate = 0

        if (string.atof(get_item(mysql_status, 'Key_blocks_used')) + string.atof(
                get_item(mysql_status, 'Key_blocks_unused'))) <> 0:
            key_blocks_used_rate = string.atof(get_item(mysql_status, 'Key_blocks_used')) / (
            string.atof(get_item(mysql_status, 'Key_blocks_used')) + string.atof(
                get_item(mysql_status, 'Key_blocks_unused')))
            key_blocks_used_rate = "%9.2f" % key_blocks_used_rate
        else:
            key_blocks_used_rate = 0

        if (string.atof(get_item(mysql_status, 'Created_tmp_disk_tables')) + string.atof(
                get_item(mysql_status, 'Created_tmp_tables'))) <> 0:
            created_tmp_disk_tables_rate = string.atof(get_item(mysql_status, 'Created_tmp_disk_tables')) / (
            string.atof(get_item(mysql_status, 'Created_tmp_disk_tables')) + string.atof(
                get_item(mysql_status, 'Created_tmp_tables')))
            created_tmp_disk_tables_rate = "%9.2f" % created_tmp_disk_tables_rate
        else:
            created_tmp_disk_tables_rate = 0

        if string.atof(max_connections) <> 0:
            connections_usage_rate = string.atof(threads_connected) / string.atof(max_connections)
            connections_usage_rate = "%9.2f" % connections_usage_rate
        else:
            connections_usage_rate = 0

        if string.atof(open_files_limit) <> 0:
            open_files_usage_rate = string.atof(open_files) / string.atof(open_files_limit)
            open_files_usage_rate = "%9.2f" % open_files_usage_rate
        else:
            open_files_usage_rate = 0

        if string.atof(table_open_cache) <> 0:
            open_tables_usage_rate = string.atof(open_tables) / string.atof(table_open_cache)
            open_tables_usage_rate = "%9.2f" % open_tables_usage_rate
        else:
            open_tables_usage_rate = 0

        # repl
        slave_status = cur.execute('show slave status;')
        if slave_status <> 0:
            role = 'slave'
            role_new = 's'
        else:
            role = 'master'
            role_new = 'm'
        now_time = datetime.datetime.now()
        ############################# INSERT INTO SERVER ##################################################
        sql = "replace into mysql_status(db_ip,db_port,connect,role,uptime,version,max_connections,max_connect_errors,open_files_limit,table_open_cache,max_tmp_tables,max_heap_table_size,max_allowed_packet,open_files,open_tables,threads_connected,threads_running,threads_created,threads_cached,connections,aborted_clients,aborted_connects,connections_persecond,bytes_received_persecond,bytes_sent_persecond,com_select_persecond,com_insert_persecond,com_update_persecond,com_delete_persecond,com_commit_persecond,com_rollback_persecond,questions_persecond,queries_persecond,transaction_persecond,created_tmp_tables_persecond,created_tmp_disk_tables_persecond,created_tmp_files_persecond,table_locks_immediate_persecond,table_locks_waited_persecond,key_buffer_size,sort_buffer_size,join_buffer_size,key_blocks_not_flushed,key_blocks_unused,key_blocks_used,key_read_requests_persecond,key_reads_persecond,key_write_requests_persecond,key_writes_persecond,innodb_version,innodb_buffer_pool_instances,innodb_buffer_pool_size,innodb_doublewrite,innodb_file_per_table,innodb_flush_log_at_trx_commit,innodb_flush_method,innodb_force_recovery,innodb_io_capacity,innodb_read_io_threads,innodb_write_io_threads,innodb_buffer_pool_pages_total,innodb_buffer_pool_pages_data,innodb_buffer_pool_pages_dirty,innodb_buffer_pool_pages_flushed,innodb_buffer_pool_pages_free,innodb_buffer_pool_pages_misc,innodb_page_size,innodb_pages_created,innodb_pages_read,innodb_pages_written,innodb_row_lock_current_waits,innodb_buffer_pool_pages_flushed_persecond,innodb_buffer_pool_read_requests_persecond,innodb_buffer_pool_reads_persecond,innodb_buffer_pool_write_requests_persecond,innodb_rows_read_persecond,innodb_rows_inserted_persecond,innodb_rows_updated_persecond,innodb_rows_deleted_persecond,query_cache_hitrate,thread_cache_hitrate,key_buffer_read_rate,key_buffer_write_rate,key_blocks_used_rate,created_tmp_disk_tables_rate,connections_usage_rate,open_files_usage_rate,open_tables_usage_rate,create_time) values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s);"
        sql2 = "insert into mysql_status_his(db_ip,db_port,connect,role,uptime,version,max_connections,max_connect_errors,open_files_limit,table_open_cache,max_tmp_tables,max_heap_table_size,max_allowed_packet,open_files,open_tables,threads_connected,threads_running,threads_created,threads_cached,connections,aborted_clients,aborted_connects,connections_persecond,bytes_received_persecond,bytes_sent_persecond,com_select_persecond,com_insert_persecond,com_update_persecond,com_delete_persecond,com_commit_persecond,com_rollback_persecond,questions_persecond,queries_persecond,transaction_persecond,created_tmp_tables_persecond,created_tmp_disk_tables_persecond,created_tmp_files_persecond,table_locks_immediate_persecond,table_locks_waited_persecond,key_buffer_size,sort_buffer_size,join_buffer_size,key_blocks_not_flushed,key_blocks_unused,key_blocks_used,key_read_requests_persecond,key_reads_persecond,key_write_requests_persecond,key_writes_persecond,innodb_version,innodb_buffer_pool_instances,innodb_buffer_pool_size,innodb_doublewrite,innodb_file_per_table,innodb_flush_log_at_trx_commit,innodb_flush_method,innodb_force_recovery,innodb_io_capacity,innodb_read_io_threads,innodb_write_io_threads,innodb_buffer_pool_pages_total,innodb_buffer_pool_pages_data,innodb_buffer_pool_pages_dirty,innodb_buffer_pool_pages_flushed,innodb_buffer_pool_pages_free,innodb_buffer_pool_pages_misc,innodb_page_size,innodb_pages_created,innodb_pages_read,innodb_pages_written,innodb_row_lock_current_waits,innodb_buffer_pool_pages_flushed_persecond,innodb_buffer_pool_read_requests_persecond,innodb_buffer_pool_reads_persecond,innodb_buffer_pool_write_requests_persecond,innodb_rows_read_persecond,innodb_rows_inserted_persecond,innodb_rows_updated_persecond,innodb_rows_deleted_persecond,query_cache_hitrate,thread_cache_hitrate,key_buffer_read_rate,key_buffer_write_rate,key_blocks_used_rate,created_tmp_disk_tables_rate,connections_usage_rate,open_files_usage_rate,open_tables_usage_rate,create_time) values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s);"
        param = (
        db.instance.ip, int(db.instance.port), connect, role, uptime, version, max_connections, max_connect_errors, open_files_limit,
        table_open_cache, max_tmp_tables, max_heap_table_size, max_allowed_packet, open_files, open_tables,
        threads_connected, threads_running, threads_created, threads_cached, connections, aborted_clients,
        aborted_connects, connections_persecond, bytes_received_persecond, bytes_sent_persecond, com_select_persecond,
        com_insert_persecond, com_update_persecond, com_delete_persecond, com_commit_persecond, com_rollback_persecond,
        questions_persecond, queries_persecond, transaction_persecond, created_tmp_tables_persecond,
        created_tmp_disk_tables_persecond, created_tmp_files_persecond, table_locks_immediate_persecond,
        table_locks_waited_persecond, key_buffer_size, sort_buffer_size, join_buffer_size, key_blocks_not_flushed,
        key_blocks_unused, key_blocks_used, key_read_requests_persecond, key_reads_persecond, key_write_requests_persecond,
        key_writes_persecond, innodb_version, innodb_buffer_pool_instances, innodb_buffer_pool_size, innodb_doublewrite,
        innodb_file_per_table, innodb_flush_log_at_trx_commit, innodb_flush_method, innodb_force_recovery,
        innodb_io_capacity, innodb_read_io_threads, innodb_write_io_threads, innodb_buffer_pool_pages_total,
        innodb_buffer_pool_pages_data, innodb_buffer_pool_pages_dirty, innodb_buffer_pool_pages_flushed,
        innodb_buffer_pool_pages_free, innodb_buffer_pool_pages_misc, innodb_page_size, innodb_pages_created,
        innodb_pages_read, innodb_pages_written, innodb_row_lock_current_waits, innodb_buffer_pool_pages_flushed_persecond,
        innodb_buffer_pool_read_requests_persecond, innodb_buffer_pool_reads_persecond,
        innodb_buffer_pool_write_requests_persecond, innodb_rows_read_persecond, innodb_rows_inserted_persecond,
        innodb_rows_updated_persecond, innodb_rows_deleted_persecond, query_cache_hitrate, thread_cache_hitrate,
        key_buffer_read_rate, key_buffer_write_rate, key_blocks_used_rate, created_tmp_disk_tables_rate,
        connections_usage_rate, open_files_usage_rate, open_tables_usage_rate,now_time)
        # print param
        mysql_exec(sql, param)
        mysql_exec(sql2, param)

        if db.check_connections:
            alarm_type = 'connections'
            if db.connection_threshold >= threads_connected:
                if record_alarm(db,alarm_type):
                    sendmail_monitor.delay(db.tag + '-too many connections', db.mail_to.split(';'), 'values:'+str(threads_connected),alarm_type)
            else:
                check_ifok(db, alarm_type)



        # check mysql connected
        connected = cur.execute("select SUBSTRING_INDEX(host,':',1) as connect_server, user connect_user,db connect_db, count(SUBSTRING_INDEX(host,':',1)) as connect_count  from information_schema.processlist where db is not null and db!='information_schema' and db !='performance_schema' group by connect_server,connect_user,connect_db;");
        if connected:
            for line in cur.fetchall():
                sql = "insert into mysql_connected(db_ip,db_port,connect_server,connect_user,connect_db,connect_count,create_time) values(%s,%s,%s,%s,%s,%s,%s);"
                param = (db.instance.ip, int(db.instance.port),line[0], line[1], line[2], line[3],now_time)
                mysql_exec(sql, param)

        #check replication
        master_thread=cur.execute("select * from information_schema.processlist where COMMAND = 'Binlog Dump' or COMMAND = 'Binlog Dump GTID';")
        slave_status=cur.execute('show slave status;')
        datalist=[]
        if master_thread >= 1:
            datalist.append(int(1))
            if slave_status <> 0:
                datalist.append(int(1))
            else:
                datalist.append(int(0))
        else:
            datalist.append(int(0))
            if slave_status <> 0:
                datalist.append(int(1))
            else:
                datalist.append(int(0))
                sql="delete from mysql_replication where db_ip=%s and db_port=%s;"
                param =(db.instance.ip,db.instance.port)
                mysql_exec(sql,param)
        if slave_status <> 0:
            gtid_mode=cur.execute("select * from information_schema.global_variables where variable_name='gtid_mode';")
            result=cur.fetchone()
            if result:
                gtid_mode=result[1]
            else:
                gtid_mode='OFF'
            datalist.append(gtid_mode)
            read_only=cur.execute("select * from information_schema.global_variables where variable_name='read_only';")
            result=cur.fetchone()
            datalist.append(result[1])
            #slave_info=cur.execute('show slave status;')
            if db.replchannel <> '0':
                slave_info=cur.execute("show slave status for channel '%s';" %(db.replchannel))
            else :
                slave_info=cur.execute('show slave status;')
            result=cur.fetchone()
            # print "result"
            # print slave_info
            master_server=result[1]
            master_port=result[3]
            slave_io_run=result[10]
            slave_sql_run=result[11]
            delay=result[32]
            current_binlog_file=result[9]
            current_binlog_pos=result[21]
            master_binlog_file=result[5]
            master_binlog_pos=result[6]
            try:
                slave_sQL_rnning_state=result[44]
            except Exception,e:
                slave_sQL_running_state="NULL"
            datalist.append(master_server)
            datalist.append(master_port)
            datalist.append(slave_io_run)
            datalist.append(slave_sql_run)
            datalist.append(delay)
            datalist.append(current_binlog_file)
            datalist.append(current_binlog_pos)
            datalist.append(master_binlog_file)
            datalist.append(master_binlog_pos)
            datalist.append(0)
            datalist.append(slave_sQL_rnning_state)

            if db.check_slave:
                if (slave_io_run == "Yes") and (slave_sql_run == "Yes"):
                    alarm_type = 'slave stop'
                    check_ifok(db, alarm_type)
                    if db.check_delay :
                        alarm_type = 'slave delay'
                        if db.delay_threshold >=delay :
                            if record_alarm(db,alarm_type):
                                sendmail_monitor.delay(db.tag + '-slave delay', db.mail_to.split(';'), 'values:'+ str(delay),alarm_type)

                        else:
                            check_ifok(db, alarm_type)
                else:
                    alarm_type='slave stop'
                    if record_alarm(db,alarm_type):
                        sendmail_monitor.delay(db.tag + '-slave stop', db.mail_to.split(';'),alarm_type, alarm_type)




        elif master_thread >= 1:
            gtid_mode=cur.execute("select * from information_schema.global_variables where variable_name='gtid_mode';")
            result=cur.fetchone()
            if result:
                gtid_mode=result[1]
            else:
                gtid_mode='OFF'
            datalist.append(gtid_mode)
            read_only=cur.execute("select * from information_schema.global_variables where variable_name='read_only';")
            result=cur.fetchone()
            datalist.append(result[1])
            datalist.append('---')
            datalist.append('---')
            datalist.append('---')
            datalist.append('---')
            datalist.append('---')
            datalist.append('---')
            datalist.append('---')
            master=cur.execute('show master status;')
            master_result=cur.fetchone()
            datalist.append(master_result[0])
            datalist.append(master_result[1])
            binlog_file=cur.execute('show master logs;')
            binlogs=0
            if binlog_file:
                for row in cur.fetchall():
                    binlogs = binlogs + row[1]
                datalist.append(binlogs)
            datalist.append('---')
        else:
            datalist=[]
        result=datalist
        if result:
            datalist.append(now_time)
            sql= "replace into mysql_replication(db_ip,db_port,is_master,is_slave,gtid_mode,read_only,master_server,master_port,slave_io_run,slave_sql_run,delay,current_binlog_file,current_binlog_pos,master_binlog_file,master_binlog_pos,master_binlog_space,slave_sql_running_state,create_time) values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"
            sql2= "insert into mysql_replication_his(db_ip,db_port,is_master,is_slave,gtid_mode,read_only,master_server,master_port,slave_io_run,slave_sql_run,delay,current_binlog_file,current_binlog_pos,master_binlog_file,master_binlog_pos,master_binlog_space,slave_sql_running_state,create_time) values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"

            param=(db.instance.ip,db.instance.port,result[0],result[1],result[2],result[3],result[4],result[5],result[6],result[7],result[8],result[9],result[10],result[11],result[12],result[13],result[14],result[15])
            mysql_exec(sql,param)
            mysql_exec(sql2, param)
        cur.close()
        conn.close()
    # except Exception, e:
    except MySQLdb.Error, e:
        print e
        time.sleep(3)
    try:
        conn = MySQLdb.connect(host=db.instance.ip, user=db.account.user, passwd=py.decrypt(db.account.passwd), port=int(db.instance.port), connect_timeout=3, charset='utf8')
        cur = conn.cursor()
        conn.select_db('information_schema')
    except MySQLdb.Error, e:
        connect = 0
        sql = "replace into mysql_status(db_ip,db_port,connect) values(%s,%s,%s)"
        param = (db.instance.ip, int(db.instance.port), connect)
        mysql_exec(sql, param)



def get_mysql_status(cursor):
    data=cursor.execute('show global status;');
    data_list=cursor.fetchall()
    data_dict={}
    for item in data_list:
        data_dict[item[0]] = item[1]
    return data_dict

def get_mysql_variables(cursor):
    data=cursor.execute('show global variables;');
    data_list=cursor.fetchall()
    data_dict={}
    for item in data_list:
        data_dict[item[0]] = item[1]
    return data_dict

def get_mysql_version(cursor):
    cursor.execute('select version();');
    return cursor.fetchone()[0]

def get_item(data_dict,item):
    try:
       item_value = data_dict[item]
       return item_value
    except:
       return '-1'