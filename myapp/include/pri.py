from django.contrib.auth.models import User,Permission,ContentType,Group
from myapp.models import Db_name,Db_group,Db_account,Db_instance,Oper_log,Login_log
from myapp.include import function as func
import uuid
#function for db_group.html
def get_full():
    dbgrouplist =  Db_group.objects.all().order_by('groupname')
    userlist = User.objects.all().order_by('username')
    dbnamelist = Db_name.objects.all().order_by('dbtag')
    return dbgrouplist,userlist,dbnamelist

def get_group_detail(groupname):
    group = Db_group.objects.get(groupname=groupname)
    a = group.dbname.all()
    b = group.account.all()
    return a,b

def set_dbgroup(groupname,dbnamesetlist,usersetlist):
    gp = Db_group.objects.get(groupname=groupname)
    new_db = Db_name.objects.filter(dbtag__in=dbnamesetlist)
    old_db = gp.dbname.all()
    new_user = User.objects.filter(username__in=usersetlist)
    old_user = gp.account.all()
    new_dbli = []
    old_dbli = []
    new_userli = []
    old_userli = []
    for i in new_db:
        new_dbli.append(i.dbtag)
    for i in old_db:
        old_dbli.append(i.dbtag)
    for i in new_user:
        new_userli.append(i.username)
    for i in old_user:
        old_userli.append(i.username)

    add_user = list(set(new_userli).difference(set(old_userli)))
    del_user = list(set(old_userli).difference(set(new_userli)))
    inter_user = list(set(old_userli).intersection(set(new_userli)))
    add_db = list(set(new_dbli).difference(set(old_dbli)))
    del_db = list(set(old_dbli).difference(set(new_dbli)))

    #del user handle
    for i in User.objects.filter(username__in=del_user):
        try:
            existdbli = get_exist_db(groupname, i, old_dbli)
            gp.account.remove(i)
            for x in old_db:
                try:
                    #if dbtag already owned by user in other group ,then don't remove
                    if x.dbtag not in existdbli:
                        x.account.remove(i)
                except Exception,e:
                    pass
        except Exception, e:
            pass

    #add user handle
    for i in User.objects.filter(username__in=add_user):
        try:
            gp.account.add(i)
            for x in new_db:
                try:
                    x.account.add(i)
                except Exception,e:
                    pass
        except Exception, e:
            pass

    #exists user handle
    for i in User.objects.filter(username__in=inter_user):
        existdbli = get_exist_db(groupname, i, old_dbli)
        for x in Db_name.objects.filter(dbtag__in=add_db) :
            if x.dbtag in existdbli:
                pass
            else:
                try:
                    x.account.add(i)
                except Exception,e:
                    pass

        for x in Db_name.objects.filter(dbtag__in=del_db) :
            if x.dbtag in existdbli:
                pass
            else:
                try:
                    x.account.remove(i)
                except Exception,e:
                    pass

    for i in Db_name.objects.filter(dbtag__in=add_db):
        try:
            gp.dbname.add(i)
        except Exception,e:
            pass

    for i in Db_name.objects.filter(dbtag__in=del_db):
        try:
            gp.dbname.remove(i)
        except Exception,e:
            pass

    return new_db,new_user


def del_dbgroup(groupname):
    gp = Db_group.objects.get(groupname=groupname)
    old_db = gp.dbname.all()
    old_user = gp.account.all()
    old_dbli = []
    for i in old_db:
        old_dbli.append(i.dbtag)
    for i in old_user:
        existdbli = get_exist_db(groupname, i, old_dbli)
        for x in old_db:
            if x.dbtag in existdbli:
                pass
            else:
                try:
                    x.account.remove(i)
                except Exception, e:
                    pass
    gp.delete()


def get_exist_db (groupname,user,old_dbli):
    # gp = Db_group.objects.get(groupname=groupname)
    exist_db = []
    for i in user.db_group_set.exclude(groupname=groupname):
        for x in i.dbname.filter(dbtag__in=old_dbli):
            exist_db.append(x.dbtag)

    return list(set(exist_db))



def create_dbgroup(groupname,dbnamesetlist,usersetlist):
    mydbname = Db_name.objects.filter(dbtag__in=dbnamesetlist)
    myuser = User.objects.filter(username__in=usersetlist)
    new_group = Db_group(groupname=groupname)
    new_group.save()
    for i in mydbname:
        try:
            new_group.dbname.add(i)
        except Exception,e:
            pass
        for x in myuser:
            try:
                i.account.add(x)
            except Exception,e:
                pass
    for i in myuser:
        try:
            new_group.account.add(i)
        except Exception,e:
            pass
    return mydbname,myuser



#u_group.html
def get_full_per():
    a = Group.objects.all().order_by('name')
    b = Permission.objects.filter(codename__istartswith='can')
    c = User.objects.all().order_by('username')
    return a,b,c

def get_ugroup_detail(groupname):
    group = Group.objects.get(name=groupname)
    a = group.permissions.all()
    b = group.user_set.all()
    return a,b

def create_ugroup(groupname,persetlist,usersetlist):
    group = Group(name=groupname)
    group.save()
    perli = Permission.objects.filter(codename__in=persetlist)
    userli = User.objects.filter(username__in=usersetlist)
    for i in perli:
        try:
            group.permissions.add(i)
        except Exception,e:
            pass
    for i in userli :
        try:
            group.user_set.add(i)
        except Exception,e:
            pass
    return perli,userli


def del_ugroup(groupname):
    group = Group.objects.get(name=groupname)
    group.delete()


#used for set_dbname.html
def get_fulldbname():
    a = Db_name.objects.all().order_by('dbtag')
    b = Db_instance.objects.all().order_by('ip','port')
    c = User.objects.exclude(username=func.public_user).order_by('username')
    return a,b,c

def get_dbtag_detail(dbtagname):
    dbtag = Db_name.objects.get(dbtag=dbtagname)
    # a = dbtag.instance.all()
    # b = dbtag.account.all()
    #return a,b
    return dbtag

def del_dbtag(dbtagname):
    dbtag = Db_name.objects.get(dbtag=dbtagname)
    for i in dbtag.db_account_set.all():
        if i.dbname.count()==1:
            i.delete()
    dbtag.delete()



def create_dbtag(dbtagname,newdbname,inssetlist,usersetlist):
    if len(dbtagname)>0 and len(newdbname)>0:
        db_name = Db_name(dbtag=dbtagname,dbname=newdbname)
        db_name.save()
        inssetlist_tmp = []
        for i in inssetlist:
            inssetlist_tmp.append(int(i))
        accli = Db_instance.objects.filter(id__in=inssetlist_tmp)
        useli = User.objects.filter(username__in=usersetlist)
    for i in accli:
        try:
            db_name.instance.add(i)
        except Exception,e:
            pass
    for i in useli:
        try:
            db_name.account.add(i)
        except Exception,e:
            pass
    return db_name

def set_dbtag(dbtagname,new_dbtagname,newdbname,inssetlist, usersetlist):
    dbtag = Db_name.objects.get(dbtag=dbtagname)
    inssetlist_tmp = []
    for i in inssetlist:
        inssetlist_tmp.append(int(i))
    accli = Db_instance.objects.filter(id__in=inssetlist_tmp)
    useli = User.objects.filter(username__in=usersetlist)
    if len(new_dbtagname) >0:
        dbtag.dbtag = new_dbtagname
        dbtag.save()
    if len(newdbname)>0:
        dbtag.dbname = newdbname
        dbtag.save()
    for i in dbtag.account.all():
        dbtag.account.remove(i)
        dbtag.save()
    for i in dbtag.instance.all():
        dbtag.instance.remove(i)
        dbtag.save()
    for i in accli:
        dbtag.instance.add(i)
    for i in useli:
        dbtag.account.add(i)
    # a = create_dbtag(dbtagname, olddbname, inssetlist, usersetlist)
    return dbtag


def set_ins(insname,setip,setport,setrole,setdbtype):
    if len(setip)>0:
        insname.ip = setip
    if len(setport)>0:
        insname.port = setport
    insname.role = setrole
    insname.db_type = setdbtype
    insname.save()
    return insname

def create_dbinstance(setip,setport,setrole,setdbtype):
    if len(setip)>0 and len(setport)>0:
        insname = Db_instance(ip=setip,port=setport,role=setrole,db_type=setdbtype)
        insname.save()
    return insname


def create_acc(tags,user,passwd,dbtagli,acclist,role):
    if len(tags)>0 and len(user)>0 and len(passwd)>0:
        account = Db_account(tags=tags,user=user,passwd=passwd,role=role)
        account.save()
    dbli = Db_name.objects.filter(dbtag__in=dbtagli)
    userli = User.objects.filter(username__in=acclist)
    for i in dbli:
        try:
            account.dbname.add(i)
        except Exception,e:
            pass
    for i in userli:
        try:
            account.account.add(i)
        except Exception,e:
            pass
    return account

def set_acc(old_account,tags,user,passwd,dbtagli,acclist,role):
    old_account.role = role
    if len(tags)>0:
        old_account.tags = tags
        old_account.save()
    if len(user)>0:
        old_account.user=user
        old_account.save()
    if len(passwd)>0:
        old_account.passwd=passwd
        old_account.save()
    for i in old_account.dbname.all():
        old_account.dbname.remove(i)
        old_account.save()
    for i in old_account.account.all():
        old_account.account.remove(i)
        old_account.save()
    for i in Db_name.objects.filter(dbtag__in=dbtagli):
        try:
            old_account.dbname.add(i)
        except Exception,e:
            pass
    for i in  User.objects.filter(username__in=acclist):
        try:
            old_account.account.add(i)
        except Exception,e:
            pass
    return  old_account


def createdb_fast(ins_set, newinsip, newinsport, newdbtag, newdbname, newname_all, newpass_all, newname_admin,newpass_admin,new_instype):
    exist_dbtag = []
    flag = 0
    for i in Db_name.objects.all():
        exist_dbtag.append(i.dbtag)
    if newdbtag in exist_dbtag:
        info = "DbTAGs already exists!"
        return  info
    if len(ins_set)>0:
        insname =  Db_instance.objects.get(id=int(ins_set))
    elif len(newinsip) >0 and len(newinsport)>0:
        flag =1
        insname = Db_instance(ip=newinsip, port=newinsport, role='all',db_type=new_instype)
        insname.save()
    else:
        info = "Please check your ip and port input!"
        return info

    try:
        user = User.objects.get(username=func.public_user)
        dbname = Db_name(dbtag=newdbtag,dbname=newdbname)
        dbname.save()
        dbname.instance.add(insname)
    #for rollback
    except Exception,e:
        info = "CREATE dbname Failed!"
        if flag == 1:
            insname.delete()
        return info
    tags = newdbtag + '+p'
    if len(newname_all) >0 and len(newpass_all)>0:
        try:
            all_account = Db_account(tags=tags, user=newname_all, passwd=newpass_all, role='all')
            all_account.save()
            all_account.account.add(user)
            all_account.dbname.add(dbname)
        # for rollback
        except Exception, e:
            info = "CREATE Failed!"
            dbname.delete()
            if flag == 1 :
                insname.delete()
            return info
    else :
        flag = 3

    if len(newname_admin)>0 and len(newpass_admin)>0:
        try:
            info = "CREATED OK!"
            admin_account = Db_account(tags=tags, user=newname_admin, passwd=newpass_admin, role='admin')
            admin_account.save()
            admin_account.account.add(user)
            admin_account.dbname.add(dbname)
        except Exception,e:
            info = e+"CREATED with admin account set failed!"
    else:
        info = "CREATE OK! with admin account not set!"
    if flag ==3 :
        info = info + " NORMAL USER not set"
    return info

def check_pubuser():
    pubuser= func.public_user
    try :
        tmp = User.objects.get(username=pubuser)
    except Exception,e:
        passwd = str(uuid.uuid1()).split('-')[0]
        user = User.objects.create_user(username=pubuser,password=passwd)
        user.save()


def init_ugroup():
    try:
        tmp = Group.objects.get(name='all')
    except Exception,e:
        try:
            b = Permission.objects.filter(codename__istartswith='can')
            gp = Group(name='all')
            gp.save()
            for i in b:
                gp.permissions.add(i)
            dmlli = ['can_insert_mysql','can_update_mysql','can_delete_mysql','can_see_execview']
            ddlli = ['can_truncate_mysql','can_drop_mysql','can_alter_mysql','can_create_mysql','can_see_execview']
            expli = ['can_mysql_query','can_export','can_see_metadata']
            queryli = ['can_mysql_query','can_see_metadata']
            logli =  ['can_log_query']
            incli = ['can_see_inception']
            metali = ['can_see_metadata']
            saltli = ['can_oper_saltapi']
            mongoQueryli = ['can_query_mongo']
            delete_task = ['can_see_taskview','can_delete_task','can_see_inception']
            admin_task = ['can_see_taskview','can_admin_task','can_see_inception']
            edit_task = ['can_see_taskview','can_update_task','can_see_inception']
            setpri = ['can_set_pri']
            querypri = ['can_query_pri']
            mysql_adminli = ['can_see_mysqladmin']
            set_group('mysql-manage', mysql_adminli)
            set_group('mysql-exec-dml',dmlli)
            set_group('mongodb-query', mongoQueryli)
            set_group('mysql-see-meta', metali)
            set_group('mysql-exec-ddl', ddlli)
            set_group('mysql-query', queryli)
            set_group('mysql-query-export', expli)
            set_group('mysql-query-log', logli)
            set_group('mysql-task-delown', delete_task)
            set_group('mysql-task-manage', admin_task)
            set_group('mysql-task-editown', edit_task)
            set_group('mysql-pri-set', setpri)
            set_group('mysql-pri-query', querypri)
            set_group('mysql-task-upload', incli)
            set_group('salt-admin', saltli)
        except Exception,e:
            pass


def set_group(name,li):
    try:
        b = Permission.objects.filter(codename__in=li)
        tmp = Group(name=name)
        tmp.save()
        for i in b:
            tmp.permissions.add(i)
    except Exception,e:
        pass



