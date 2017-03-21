# coding=utf-8
from mypro import settings
import urllib2, urllib, json,ssl,MySQLdb,socket
from salt.models import Saltrecord
import datetime

def salt_query(sql):
    try:
        host = settings.SALT_DATABASE['HOST']
        port = settings.SALT_DATABASE['PORT']
        user = settings.SALT_DATABASE['USER']
        passwd = settings.SALT_DATABASE['PASSWORD']
        dbname = settings.SALT_DATABASE['NAME']
        conn=MySQLdb.connect(host=host,user=user,passwd=passwd,port=int(port),connect_timeout=5,charset='utf8')
        conn.select_db(dbname)
        cursor = conn.cursor()
        count=cursor.execute(sql)
        # index=cursor.description
        # col=[]
        # #get column name
        # for i in index:
        #     col.append(i[0])
        result=cursor.fetchall()
        # result=cursor.fetchmany(size=int(limitnum))
        cursor.close()
        conn.close()
        return (result,count)
    except Exception,e:
        return([str(e)],''),1


class SaltAPI(object):
    ssl._create_default_https_context = ssl._create_unverified_context

    def __init__(self):
        self.__url = settings.SALT_API_URL.rstrip('/')
        self.__user = settings.SALT_API_USER
        self.__password = settings.SALT_API_PASSWD
        self.__token_id = self.saltLogin()

    def saltLogin(self):
        params = {'eauth': 'pam', 'username': self.__user, 'password': self.__password}
        encode = urllib.urlencode(params)
        obj = urllib.unquote(encode)
        headers = {'X-Auth-Token': ''}
        url = self.__url + '/login'
        req = urllib2.Request(url, obj, headers)
        opener = urllib2.urlopen(req)
        content = json.loads(opener.read())
        try:
            token = content['return'][0]['token']
            return token
        except KeyError:
            raise KeyError

    def postRequest(self, obj, prefix='/'):
        url = self.__url + prefix
        headers = {'X-Auth-Token': self.__token_id}
        req = urllib2.Request(url, obj, headers)
        opener = urllib2.urlopen(req)
        content = json.loads(opener.read())
        return content

    def asyncMasterToMinion(self, tgt, fun, arg,group=0):
        '''
        异步执行，当target为部分minion时，Master操作Minion；
        :param target: 目标服务器ID组成的字符串；
        :param fun: 使用的salt模块，如state.sls, cmd.run
        :param arg: 传入的命令或sls文件
        :return: jid字符串
        '''

        if tgt == '*':
            params = {'client': 'local_async', 'tgt': tgt, 'fun': fun, 'arg': arg,'ret':'mysql'}
        else:
            if group==1:
                params = {'client': 'local_async', 'tgt': tgt, 'fun': fun, 'arg': arg, 'expr_form': 'nodegroup','ret': 'mysql'}
            else:
                if is_valid_ip(tgt):
                    params = {'client': 'local_async', 'tgt': tgt, 'fun': fun, 'arg': arg, 'expr_form': 'ipcidr','ret':'mysql'}
                else:
                    params = {'client': 'local_async', 'tgt': tgt, 'fun': fun, 'arg': arg, 'expr_form': 'list','ret':'mysql'}
        obj = urllib.urlencode(params)
        content = self.postRequest(obj)
        jid = content['return'][0]['jid']
        return jid




    def masterToMinionContent(self, tgt, fun, arg):
        '''
            Master控制Minion，返回的结果是内容，不是jid；
            目标参数tgt是一个如下格式的字符串：'*' 或 'zhaogb-201, zhaogb-202, zhaogb-203, ...'
        '''
        if tgt == '*':
            params = {'client': 'local', 'tgt': tgt, 'fun': fun, 'arg': arg,'ret':'mysql'}
        else:
            params = {'client': 'local', 'tgt': tgt, 'fun': fun, 'arg': arg, 'expr_form': 'ipcidr','ret':'mysql'}
        obj = urllib.urlencode(params)
        content = self.postRequest(obj)
        result = content['return'][0]
        return result

    # 定义不加参数的命令
    def remote_noarg_execution_sin(self, tgt, fun):
        ''' Execute commands without parameters '''
        params = {'client': 'local', 'tgt': tgt, 'fun': fun,'ret':'mysql'}
        obj = urllib.urlencode(params)
        content = self.postRequest(obj)
        ret = content['return'][0][tgt]
        return ret

    # 定义获取所有客户端KEY函数
    def list_all_key(self):
        '''
           返回所有Minion keys；
           分别为 已接受、待接受、已拒绝；
           :return: [u'local', u'minions_rejected', u'minions_denied', u'minions_pre', u'minions']
       '''
        params = {'client': 'wheel', 'fun': 'key.list_all'}
        obj = urllib.urlencode(params)
        content = self.postRequest(obj)
        # minions = content['return'][0]['data']['return']['minions']
        # minions_pre = content['return'][0]['data']['return']['minions_pre']
        # minions_rej = content['return'][0]['data']['return']['minions_rejected']
        # minions_den = content['return'][0]['data']['return']['minions_denied']
        minions = content['return'][0]['data']['return']
        return minions

    def delete_key(self, node_name):
        params = {'client': 'wheel', 'fun': 'key.delete', 'match': node_name}
        obj = urllib.urlencode(params)
        content = self.postRequest(obj)
        ret = content['return'][0]['data']['success']
        return ret

    def accept_key(self, node_name):
        params = {'client': 'wheel', 'fun': 'key.accept', 'match': node_name}
        obj = urllib.urlencode(params)
        content = self.postRequest(obj)
        ret = content['return'][0]['data']['success']
        return ret

    def reject_key(self, node_name):
        params = {'client': 'wheel', 'fun': 'key.reject', 'match': node_name}
        obj = urllib.urlencode(params)
        content = self.postRequest(obj)
        ret = content['return'][0]['data']['success']
        return ret

    # def actionKyes(self, keystrings, action):
    #     '''
    #     对Minion keys 进行指定处理；
    #     :param keystrings: 将要处理的minion id字符串；
    #     :param action: 将要进行的处理，如接受、拒绝、删除；
    #     :return:
    #     {"return": [{"tag": "salt/wheel/20160322171740805129", "data": {"jid": "20160322171740805129", "return": {}, "success": true, "_stamp": "2016-03-22T09:17:40.899757", "tag": "salt/wheel/20160322171740805129", "user": "zhaogb", "fun": "wheel.key.delete"}}]}
    #     '''
    #     func = 'key.' + action
    #     params = {'client': 'wheel', 'fun': func, 'match': keystrings}
    #     obj = urllib.urlencode(params)
    #     content = self.postRequest(obj)
    #     ret = content['return'][0]['data']['success']
    #     return ret
    #
    # def acceptKeys(self, keystrings):
    #     '''
    #     接受Minion发过来的key；
    #     :return:
    #     '''
    #     params = {'client': 'wheel', 'fun': 'key.accept', 'match': keystrings}
    #     obj = urllib.urlencode(params)
    #     content = self.postRequest(obj)
    #     ret = content['return'][0]['data']['success']
    #     return ret
    #
    # def deleteKeys(self, keystrings):
    #     '''
    #     删除Minion keys；
    #     :param node_name:
    #     :return:
    #     '''
    #     params = {'client': 'wheel', 'fun': 'key.delete', 'match': keystrings}
    #     obj = urllib.urlencode(params)
    #     content = self.postRequest(obj)
    #     ret = content['return'][0]['data']['success']
    #     return ret

    def runner_status(self, arg):
        ''' Return minion status '''
        params = {'client': 'runner', 'fun': 'manage.' + arg}
        obj = urllib.urlencode(params)
        content = self.postRequest(obj)['return'][0]
        return content


    def remote_noarg_execution_mul(self, tgt, fun,group=0):
        ''' Execute commands without parameters '''
        if tgt=='*':
            params = {'client': 'local', 'tgt': tgt, 'fun': fun, 'ret': 'mysql'}
        else:
            if group==1:
                params = {'client': 'local', 'tgt': tgt, 'fun': fun, 'ret': 'mysql','expr_form': 'nodegroup'}
            else:
                if is_valid_ip(tgt):
                    params = {'client': 'local', 'tgt': tgt, 'fun': fun, 'ret': 'mysql', 'expr_form': 'ipcidr'}
                else:
                    params = {'client': 'local', 'tgt': tgt, 'fun': fun, 'ret': 'mysql', 'expr_form': 'list'}
        obj = urllib.urlencode(params)
        content = self.postRequest(obj)
        return content['return'][0].keys(),content['return'][0].values()

def get_host_list(se_host,isgp):
    sapi_1 = SaltAPI()

    if se_host == '*':
        return sapi_1.runner_status('status')['up']
    else:
        if isgp == 1:
            x, y = sapi_1.remote_noarg_execution_mul(se_host, 'test.ping',1)
            return x
        else:
            x, y = sapi_1.remote_noarg_execution_mul(se_host, 'test.ping')
            return x

def is_valid_ip(ip):
    """Returns true if the given string is a well-formed IP address.

    Supports IPv4 and IPv6.
    """
    if not ip or '\x00' in ip:
        # getaddrinfo resolves empty strings to localhost, and truncates
        # on zero bytes.
        return False
    try:
        res = socket.getaddrinfo(ip, 0, socket.AF_UNSPEC,
                                 socket.SOCK_STREAM,
                                 0, socket.AI_NUMERICHOST)
        return bool(res)
    except socket.gaierror as e:
        if e.args[0] == socket.EAI_NONAME:
            return False
        raise
    return True


def record_salt(user,jid,fun,tgt,arg):
    create_time = datetime.datetime.now()
    log = Saltrecord(user=user, operation=fun, jid=jid, tgt=tgt,arg=arg,create_time=create_time)
    log.save()

def main():
    # 以下是用来测试saltAPI类的部分
    print is_valid_ip('10.1.70.22')
    sapi = SaltAPI()
    params = {'client': 'local', 'fun': 'run.cmd', 'tgt': '*'}
    # params = {'client':'local', 'fun':'test.ping', 'tgt':'某台服务器的key'}
    # params = {'client':'local', 'fun':'test.echo', 'tgt':'某台服务器的key', 'arg1':'hello'}
    # params = {'client':'local', 'fun':'test.ping', 'tgt':'某组服务器的组名', 'expr_form':'nodegroup'}
    #test = sapi.saltCmd(params)
    print "hellp"
    print sapi.asyncMasterToMinion('*','test.ping','none_arg')
    x= sapi.list_all_key()
    print x
    sapi1 = SaltAPI()
    a = sapi.runner_status('status')['up']
    print a


if __name__ == '__main__':
    main()