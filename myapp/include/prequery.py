#!/bin/env python
#-*-coding:utf-8-*-
import MySQLdb,sys,string,time,datetime

from multiprocessing import Process
import os

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
    #config.readfp(open('./myapp/etc/config.ini','r'))
    config.readfp(open('../etc/config.ini','r'))
    config_value=config.get(group,config_name).strip(' ').strip('\'').strip('\"')
    return config_value

def filters(data):
    return data.strip(' ').strip('\n').strip('\br')

host = get_config('settings','host')
port = get_config('settings','port')
user = 'test'
passwd = 'test'
dbname = 'test'

def mysql_exec(sql):
    try:
        conn=MySQLdb.connect(host=host,user=user,passwd=passwd,port=int(port),connect_timeout=5,charset='utf8')
        conn.select_db(dbname)
        curs = conn.cursor()

        x=curs.execute(sql)
        conn.commit()
        curs.close()
        conn.close()
        return  "select 'Don\\'t have permission to \"delete\"'"
    except Exception,e:
        print "what the"
        print "select \"" +str(e).replace('"',"\"")+"\""
        print "the fuck"
        print "mysql execute: " + str(e)

def mysql_query(sql,user=user,passwd=passwd,host=host,port=int(port),dbname=dbname):
    try:
        limitnum=100
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

def incep_exec(sqltext,user,passwd,host,port,dbname):
    port=int(port)
    dbname=dbname.encode("utf8")
    sql1="/*--user=%s;--password=%s;--host=%s;--enable-execute;--port=%d;*/\
            inception_magic_start;\
            use %s;"% (user,passwd,host,port,dbname)
    sql2='inception_magic_commit;'
    sql = sql1 + sqltext + sql2
    try:
        conn=MySQLdb.connect(host='10.1.70.222',user='',passwd='',db='',port=6669,use_unicode=True, charset="utf8")
        cur=conn.cursor()
        ret=cur.execute(sql)
        result=cur.fetchall()
        #num_fields = len(cur.description)
        field_names = [i[0] for i in cur.description]
        #print field_names
        #for row in result:
        #    print row[0], "|",row[1],"|",row[2],"|",row[3],"|",row[4],"|",row[5],"|",row[6],"|",row[7],"|",row[8],"|",row[9],"|",row[10]
        cur.close()
        conn.close()
    except MySQLdb.Error,e:
        return([str(e)],''),['error']
    return result,field_names
    #return result[1][4].split("\n")
 #create table t2 (id int) ;insert into t1 VALUES (2);


# 子进程要执行的代码
def run_proc(name,name2):
    print 'Run child process %s (%s)...' % (name, name2)
    print name2

def run_test(name):
    run_proc(name,'testchangjingxiu')

def main():
    x,y= mysql_query('select * from item_infor')
    print type(x)
    for i in x:
        print x
    print y
if __name__=='__main__':
    main()