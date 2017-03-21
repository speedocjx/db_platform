#coding=UTF-8
import MySQLdb,sys,string,time,datetime,uuid,pymongo,json
from django.contrib.auth.models import User
from myapp.models import Db_name,Db_account,Db_instance
from myapp.etc import config
from django.core.serializers.json import DjangoJSONEncoder

public_user = config.public_user
export_limit = int(config.export_limit)
def get_mongodb_list(username,tag='tag',search=''):
    dbtype='mongodb'
    host_list = []
    if len(search) ==0:
        if (tag=='tag'):
            a = User.objects.get(username=username)
            #如果没有对应role='read'或者role='all'的account账号，则不显示在下拉菜单中
            for row in a.db_name_set.all().order_by("dbtag"):
                if row.db_account_set.all().filter(role__in=['read','all']):
                    if row.instance.all().filter(role__in=['read','all']).filter(db_type=dbtype):
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
                    if row.instance.all().filter(role__in=['write','all']).filter(db_type=dbtype):
                        host_list.append(row.dbtag)
    elif len(search) > 0:
        if (tag=='tag'):
            a = User.objects.get(username=username)
            #如果没有对应role='read'或者role='all'的account账号，则不显示在下拉菜单中
            for row in a.db_name_set.filter(dbname__contains=search).order_by("dbtag"):
                if row.db_account_set.all().filter(role__in=['read','all']):
                    if row.instance.all().filter(role__in=['read','all']).filter(db_type=dbtype):
                        host_list.append(row.dbtag)
        elif (tag=='log'):
            for row in Db_name.objects.values('dbtag').distinct().order_by("dbtag"):
                host_list.append(row['dbtag'])
        elif (tag=='exec'):
            a = User.objects.get(username=username)
            #如果没有对应role='write'或者role='all'的account账号，则不显示在下拉菜单中
            for row in a.db_name_set.filter(dbname__contains=search).order_by("dbtag"):
                if row.db_account_set.all().filter(role__in=['write','all']):
            #排除只读实例
                    if row.instance.all().filter(role__in=['write','all']).filter(db_type=dbtype):
                        host_list.append(row.dbtag)
    return host_list


def get_mongo_coninfo(hosttag,useraccount):

    a = Db_name.objects.filter(dbtag=hosttag)[0]
    # a = Db_name.objects.get(dbtag=hosttag)
    tar_dbname = a.dbname
    try:
        if a.instance.all().filter(role='read')[0]:
            tar_host = a.instance.all().filter(role='read')[0].ip
            tar_port = a.instance.all().filter(role='read')[0].port
    # 如果没有设置或没有role=read，则选择第一个读到的all实例读取
    except Exception, e:
        tar_host = a.instance.filter(role='all')[0].ip
        tar_port = a.instance.filter(role='all')[0].port
        # tar_host = a.instance.all()[0].ip
        # tar_port = a.instance.all()[0].port
    for i in a.db_account_set.all():
        if i.role != 'write' and i.role != 'admin':
            # find the specified account for the user
            if i.account.all().filter(username=useraccount):
                tar_username = i.user
                tar_passwd = i.passwd
                break
    # not find specified account for the user ,specified the public account to the user
    if not vars().has_key('tar_username'):
        for i in a.db_account_set.all():
            if i.role != 'write' and i.role != 'admin':
                # find the specified account for the user
                if i.account.all().filter(username=public_user):
                    tar_username = i.user
                    tar_passwd = i.passwd
                    break
    return tar_host,tar_port,tar_username,tar_passwd,tar_dbname


def get_db_info(hosttag,useraccount):
    tar_host, tar_port, tar_username, tar_passwd, tar_dbname = get_mongo_coninfo(hosttag, useraccount)
    connect = pymongo.MongoClient(tar_host, int(tar_port))
    db = connect[tar_dbname]
    try:
        db.authenticate(tar_username, tar_passwd)
    except Exception, e:
        pass
    results = db.command({'dbstats': 1})
    return results

def get_tb_info(hosttag,tbname,useraccount):
    tar_host, tar_port, tar_username, tar_passwd, tar_dbname = get_mongo_coninfo(hosttag, useraccount)
    connect = pymongo.MongoClient(tar_host, int(tar_port))
    db = connect[tar_dbname]
    try:
        db.authenticate(tar_username, tar_passwd)
    except Exception, e:
        pass
    results = db.command({'collstats': tbname})
    return results

def get_tbindex_info(hosttag,tbname,useraccount):
    tar_host, tar_port, tar_username, tar_passwd, tar_dbname = get_mongo_coninfo(hosttag, useraccount)
    connect = pymongo.MongoClient(tar_host, int(tar_port))
    db = connect[tar_dbname]
    try:
        db.authenticate(tar_username, tar_passwd)
    except Exception, e:
        pass
    collection = db[tbname]
    results = collection.index_information()
    return results

def get_mongo_collection(hosttag,useraccount):
    try:
        tar_host, tar_port, tar_username, tar_passwd, tar_dbname = get_mongo_coninfo(hosttag, useraccount)
        # 此处根据tablename获取其他信息
        connect = pymongo.MongoClient(tar_host, int(tar_port))
        db = connect[tar_dbname]
        try:
            db.authenticate(tar_username, tar_passwd)
        except Exception, e:
            pass
        results = db.collection_names()
    except Exception, e:
        results,col = ([str(e)],''),['error']
    return results


def get_mongo_data(b,hosttag,tbname,useraccount):
    try:
        num = int(User.objects.get(username=useraccount).user_profile.export_limit)
    except Exception, e:
        num = export_limit
    try:
        tar_host, tar_port, tar_username, tar_passwd, tar_dbname = get_mongo_coninfo(hosttag, useraccount)
        #此处根据tablename获取其他信息
        connect = pymongo.MongoClient(tar_host,int(tar_port))
        db=connect[tar_dbname]
        try:
            db.authenticate(tar_username,tar_passwd)
        except Exception,e:
            pass
        #tablename = tablename
        collection = db[tbname]
        #a = '''{'currTime': 1477371861706}'''
        resulta = collection.find(eval(b),{"_id":0}).limit(num)
        # resulta = collection.find().limit(20)
        #results = db.collection_names()    #获取所有tables名字
        results = []
        for recordjson in resulta:
            #resultdict = {}
            #for k,v in recordjson:
            #    resultdict[k] = v.encode('gb18030')    #["ObjectId('580ee6e6f3de9821b20e57db') is not JSON serializable"]
            results.append(json.dumps(recordjson,ensure_ascii=False,cls=DjangoJSONEncoder))
            #results.append(recordjson)
    except Exception, e:
        results = (['error'],'')
    return results

if __name__ == '__main__':
    #x="insert /*sdfs*/into mysql.test ;truncate table mysql.db;rename mysql.db ;rename asdf;delete from  `msql`.sa set ;delete ignore from t1 mysql.test values sdasdf;insert into ysql.user values()"
    # print x
    #x=" /*! */; select /**/ #asdfasdf; \nfrom mysql_replication_history;"
    #x = " insert into item_infor (id,name) values(7,'t\\'e\"st');drop t * from test;"

    print  get_mongo_data('{"_class" : "com.mongodb.BasicDBObject"}','mongodb-easemob','message','root')