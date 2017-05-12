import sqlparse
from sqlparse.sql import IdentifierList, Identifier
from sqlparse.tokens import Keyword, DML

exceptlist = ["'","`","\""]

def sql_init_filter(sqlfull):
    tmp = oldp = sql = ''
    sqllist = []
    flag = 0
    sqlfull = sqlfull.replace('\r','\n').strip()
    try:
        if sqlfull[-1]!=";":
            sqlfull = sqlfull + ";"
    except Exception,e:
        pass
    for i in sqlfull.split('\n'):
        if len(i)>=2:
            if i[0] == '-' and i[1] == '-' :
                continue
        if len(i)>=1:
            if i[0] == '#' :
                continue
        if len(i)!=0:
            tmp = tmp + i + '\n'

    sqlfull = tmp
    tmp = ''
    i=0
    while i<= (0 if len(sqlfull)==0 else len(sqlfull)-1):
        if sqlfull[i] =='*' and oldp == '/'and flag == 0 :
            flag = 2
            #sql = sql + sqlfull[i]
            sql = sql[:-1]+' '
        elif sqlfull[i] == '/' and oldp == '*' and flag == 2:
            flag = 0
            #sql = sql + sqlfull[i]
            sql = sql[:-1]+ ' '
        elif sqlfull[i] == tmp and flag == 1 and oldp != "\\":
            flag = 0
            sql = sql + sqlfull[i]
            tmp=''
            # print sql
            # print "what hellp"
        elif sqlfull[i] in exceptlist and flag == 0 and oldp != "\\":
            tmp = sqlfull[i]
            flag = 1
            sql = sql + sqlfull[i]
            # print sql
            # print "hello"
        elif sqlfull[i] == ';' and flag == 0:
            sql = sql + sqlfull[i]
            if len(sql) > 1:
                sqllist.append(sql)
            sql = ''
        # eliminate '#' among the line
        elif sqlfull[i] == '#' and flag == 0:
            flag =3
        elif flag==3:
            if sqlfull[i] == '\n':
                flag=0
                sql = sql + sqlfull[i]
        elif flag!=2:
            sql = sql + sqlfull[i]
        oldp = sqlfull[i]
        i=i+1
    return sqllist


def get_sql_detail(sqllist,flag):

    query_type = ['desc','describe','show','select','explain']
    dml_type = ['insert', 'update', 'delete', 'create', 'alter','rename', 'drop', 'truncate', 'replace']
    if flag == 1:
        list_type = query_type
    elif flag ==2:
        list_type = dml_type
    typelist = []
    i = 0
    while i <= (0 if len(sqllist) == 0 else len(sqllist) - 1):
        try:
            mylist = sqllist[i].split()
            mylen = len(mylist)
            type = mylist[0].lower()
            if len(type)> 1:
                if type in list_type:
                    myflag=0
                    # if type == 'use' and mylist[1].lower().split(';')[0] in ['mysql']:
                    #     print mylist[1]
                    #     print 'fuck'
                    #     sqllist.pop(i)
                    #     continue

                    if type == 'create' or type == 'drop' or type == 'alter':
                        # filter create ,alter or drop database,user
                        if mylist[1].lower() in ['database','schema','user']:
                            sqllist.pop(i)
                            continue
                        #filter ddl for mysql.* table
                        elif mylist[1].lower() =='table':
                            if mylist[2].lower().split('.')[0].lower() in ['mysql','`mysql`']:
                                sqllist.pop(i)
                                continue
                        elif mylist[1].lower() in ['temporary','ignore']:
                            if  mylist[2].lower() =='table' and mylist[3].lower().split('.')[0].lower() in ['mysql', '`mysql`']:
                                sqllist.pop(i)
                                continue

                    if type in ['rename', 'truncate'] and mylen >= 2:
                        tmp_i = 1
                        # only filter the first four is enough
                        while tmp_i <= (2 if mylen > 2 else mylen):
                            # print mylist[i].lower()
                            if mylist[tmp_i].lower() in ['table']:
                                tmp_i = tmp_i + 1
                                continue
                            else:
                                # print mylist[tmp_i].lower()
                                if mylist[tmp_i].lower().split('.')[0].lower() in ['mysql', '`mysql`']:
                                    myflag = 1
                                break
                            tmp_i = tmp_i + 1
                    if myflag == 1:
                        sqllist.pop(i)
                        continue



                    #filter dml for mysql.* table
                    if type in ['insert','replace'] and mylen >= 2:
                        tmp_i = 1
                        #only filter the first four is enough
                        while tmp_i <=(4 if mylen>4 else mylen):
                            # print mylist[i].lower()
                            if mylist[tmp_i].lower() in ['low_priority','delayed','high_priority','ignore','into']:
                                tmp_i = tmp_i + 1
                                continue
                            else:
                                if mylist[tmp_i].lower().split('.')[0].lower() in ['mysql','`mysql`']:
                                    myflag=1
                                break
                            tmp_i=tmp_i+1
                    if myflag==1:
                        sqllist.pop(i)
                        continue


                    if type in ['delete'] and mylen >= 2:
                        tmp_i = 1
                        #only filter the first four is enough
                        while tmp_i <=(4 if mylen>4 else mylen):
                            # print mylist[tmp_i].lower()
                            if mylist[tmp_i].lower() in ['low_priority','quick','from','ignore']:
                                tmp_i = tmp_i + 1
                                continue
                            else:
                                if mylist[tmp_i].lower().split('.')[0].lower() in ['mysql','`mysql`']:
                                    myflag=1
                                break
                            tmp_i=tmp_i+1

                    if myflag==1:
                        sqllist.pop(i)
                        continue

                    if type in ['update'] and mylen >= 2:
                        tmp_i = 1
                        #only filter the first four is enough
                        while tmp_i <=(3 if mylen>3 else mylen):
                            # print mylist[i].lower()
                            if mylist[tmp_i].lower() in ['low_priority','ignore']:
                                tmp_i = tmp_i + 1
                                continue
                            else:
                                for up in mylist[tmp_i].lower().split(','):
                                    # print up
                                    if up.split('.')[0].lower() in ['mysql','`mysql`']:
                                        myflag=1
                                        break
                            if myflag == 1:
                                break
                            tmp_i=tmp_i+1
                    if myflag==1:
                        sqllist.pop(i)
                        continue

                    typelist.append(type)
                    i = i + 1
                else:
                    sqllist.pop(i)
            else:
                sqllist.pop(i)
        except:
            #sqllist.pop(i)
            i = i + 1

    return sqllist
#
# def sql_init_filter(sqlfull):
#     tmp = oldp = sql = ''
#     sqllist = []
#     flag = 0
#     sqlfull = sqlfull.replace('\r','\n').strip()
#     try:
#         if sqlfull[-1]!=";":
#             sqlfull = sqlfull + ";"
#     except Exception,e:
#         pass
#     for i in sqlfull.split('\n'):
#         if len(i)>=2:
#             if i[0] == '-' and i[1] == '-' :
#                 continue
#         if len(i)>=1:
#             if i[0] == '#' :
#                 continue
#         if len(i)!=0:
#             tmp = tmp + i + '\n'
#
#     sqlfull = tmp
#     tmp = ''
#     i=0
#     while i<= (0 if len(sqlfull)==0 else len(sqlfull)-1):
#         if sqlfull[i] =='*' and oldp == '/'and flag == 0 :
#             flag = 2
#             sql = sql + sqlfull[i]
#         elif sqlfull[i] == '/' and oldp == '*' and flag == 2:
#             flag = 0
#             sql = sql + sqlfull[i]
#         elif sqlfull[i] == tmp and flag == 1:
#             flag = 0
#             sql = sql + sqlfull[i]
#             tmp=''
#         elif sqlfull[i] in exceptlist and flag == 0 and oldp != "\\":
#             tmp = sqlfull[i]
#             flag = 1
#             sql = sql + sqlfull[i]
#         elif sqlfull[i] == ';' and flag == 0:
#             sql = sql + sqlfull[i]
#             if len(sql) > 1:
#                 sqllist.append(sql)
#             sql = ''
#         # eliminate '#' among the line
#         elif sqlfull[i] == '#' and flag == 0:
#             flag =3
#         elif flag==3:
#             if sqlfull[i] == '\n':
#                 flag=0
#                 sql = sql + sqlfull[i]
#         else:
#             sql = sql + sqlfull[i]
#         oldp = sqlfull[i]
#         i=i+1
#     return sqllist
#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright (C) 2016 Andi Albrecht, albrecht.andi@gmail.com
#
# This example is part of python-sqlparse and is released under
# the BSD License: https://opensource.org/licenses/BSD-3-Clause
#
# This example illustrates how to extract table names from nested
# SELECT statements.
#
# See:
# http://groups.google.com/group/sqlparse/browse_thread/thread/b0bd9a022e9d4895


class Sqlparse():

    def __init__(self,sql):
        self.sql = sql

    def is_subselect(self,parsed):
        if not parsed.is_group:
            return False
        for item in parsed.tokens:
            if item.ttype is DML and item.value.upper() == 'SELECT':
                return True
        return False


    def extract_from_part(self,parsed):
        from_seen = False
        for item in parsed.tokens:
            if from_seen:
                if self.is_subselect(item):
                    for x in self.extract_from_part(item):
                        yield x
                elif item.ttype is Keyword:
                    raise StopIteration
                else:
                    yield item
            elif item.ttype is Keyword and item.value.upper() == 'FROM':
                from_seen = True


    def extract_table_identifiers(self,token_stream):
        for item in token_stream:
            if isinstance(item, IdentifierList):
                for identifier in item.get_identifiers():
                    yield identifier.get_real_name()
            elif isinstance(item, Identifier):
                yield item.get_real_name()
            # It's a bug to check for Keyword here, but in the example
            # above some tables names are identified as keywords...
            elif item.ttype is Keyword:
                yield item.value


    def extract_tables(self):
        # print sqlparse.parse(self.sql)[0]
        stream = self.extract_from_part(sqlparse.parse(self.sql)[0])
        # print stream
        return list(self.extract_table_identifiers(stream))



if __name__ == '__main__':
    x = " insert into item_infor (id,name) values(7,'t\\'e\"st'); drop /*sdf\n\n\n\n\n\fd*/  abase ;#adfadfaf \n select adf; create;alter table mysql.user ; create /*\\'\" test */ table test (id int ,name varchar(30)) comment 'asdasdasd';\n;/*! test &&\''& */\r\n;\r\n/*!40101 SET character_set_client = @saved_cs_client */;alter  user asdf sdf;\r;create table test ;\n;;;select /* force index test \'\"*/ * from test ;"
    #x="insert /*sdfs*/into mysql.test ;truncate table mysql.db;rename mysql.db ;rename asdf;delete from  `msql`.sa set ;delete ignore from t1 mysql.test values sdasdf;insert into ysql.user values()"
    # print x
    #x=" /*! */; select /**/ #asdfasdf; \nfrom mysql_replication_history;"
    #x = " insert into item_infor (id,name) values(7,'t\\'e\"st');drop t * from test;"
    sqllist = sql_init_filter(x)
    for i in sqllist:
        print i
    print  get_sql_detail(sqllist,2)
    test= Sqlparse(x)
    print test.extract_tables()
    # tables = ', '.join(extract_tables(sql))
    # print('Tables: {0}'.format(tables))
