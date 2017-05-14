import sqlparse
from sqlparse.sql import IdentifierList, Identifier
from sqlparse.tokens import Keyword, DML
from django.contrib.auth.models import User
from blacklist.models import Tb_blacklist



class Sqlparse():

    def __init__(self,sql=None):
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

    #black white list check
    def check_query_table(self,dbtag,username):
        list = Tb_blacklist.objects.filter(dbtag=dbtag)
        if list :
            #user in white list
            if User.objects.get(username=username) in list[0].user_permit.all():
                existTb=[]
            else :
                #if table in black list
                blackTblist = list[0].tbname.split(',')
                parser = Sqlparse(self.sql)
                tblist = parser.extract_tables()
                existTb = [val for val in blackTblist if val in tblist]
            if existTb:
                return True,existTb
        return False,[]
