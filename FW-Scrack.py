#coding:utf-8

import getopt
import sys
import Queue
import threading
import socket
import urllib2
import time
import os
import re
import ftplib
import hashlib
import struct
import binascii
import telnetlib
import array

queue = Queue.Queue()
mutex = threading.Lock()
TIMEOUT = 10
I = 0
USER_DIC = {
    "ftp":['www','admin','root','db','wwwroot','data','web','ftp'],
    "mysql":['root'],
    "mssql":['sa'],
    "telnet":['administrator','admin','root'],
    "postgresql":['postgres','admin'],
    "redis":['null'],
    "mongodb":['null'],
    "memcached":['null'],
    "elasticsearch":['null']
}
PASSWORD_DIC = ['123456','admin','root','password','123123','123','1','{user}','{user}{user}','{user}1','{user}123','{user}2018','{user}2019','{user}2020','{user}2021','{user}2016','{user}2015','{user}2017','{user}2014','{user}!','','P@ssw0rd!!','qwa123','12345678','test','123qwe!@#','123456789','123321','1314520','666666','woaini','fuckyou','000000','1234567890','8888888','qwerty','1qaz2wsx','abc123','abc123456','1q2w3e4r','123qwe','159357','p@ssw0rd','p@55w0rd','password!','p@ssw0rd!','password1','r00t','tomcat','apache','system','huawei','zte','1234']
REGEX = [['ftp', '21', '^220.*?ftp|^220-|^220 Service|^220 FileZilla'],  ['telnet', '23', '^\\xff[\\xfa-\\xfe]|^\\x54\\x65\\x6c|Telnet'],['mssql', '1433', ''], ['mysql', '3306', '^.\\0\\0\\0.*?mysql|^.\\0\\0\\0\\n|.*?MariaDB server'], ['postgresql', '5432', ''], ['redis', '6379', '-ERR|^\\$\\d+\\r\\nredis_version'], ['elasticsearch', '9200', ''], ['memcached', '11211', '^ERROR'], ['mongodb', '27017', '']]
def scan_port(host,port):
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((str(host),int(port)))
        log('portscan',host,port)
    except Exception,e:
        return False
    try:
        data = sock.recv(512)
        if len(data) > 2:
            return data
        else:
            sock.send('a\n\n')
            data = sock.recv(512)
            sock.close()
            if len(data) > 2:
                return data
            else:
                return 'NULL'
    except Exception,e:
        sock.close()
        return 'NULL'
def log(scan_type,host,port,info=''):
    mutex.acquire()
    time_str = time.strftime('%X', time.localtime( time.time()))
    if scan_type == 'portscan':
        erase()
        print "[%s] \033[0;36;40m\t%s:%d\033[0m \033[0;32;40m\t开启\033[0m" % (time_str,host,int(port))
    elif scan_type == 'discern':
        erase()
        print "[%s] \033[0;36;40m\t%s:%d\033[0m \033[0;32;40m\t%s\033[0m" % (time_str,host,int(port),info)
    elif scan_type == 'active':
        erase()
        print "[%s] \033[0;36;40m\t%s\033[0m \033[0;32;40m\t活跃\033[0m" % (time_str, host)
    elif info:
        log = "[%s] \033[0;36;40m\t%s:%d\033[0m \033[0;32;40m\t%s %s\033[0m"%(time_str,host,int(port),scan_type,info)
        erase()
        print log
        log_file = open('result.log','a')
        log_file.write(log+"\r\n")
        log_file.close()
    mutex.release()
def server_discern(host,port,data):
    for mark_info in REGEX:
        try:
            name,default_port,reg = mark_info
            if reg and data <> 'NULL':
                matchObj = re.search(reg,data,re.I|re.M)
                if matchObj:
                    return name
            elif int(default_port) == int(port):
                return name
        except Exception,e:
            print e
            continue
def pass_crack(server_type,host,port):
    m = Crack(host,port,server_type,TIMEOUT)
    return m.run()
def get_password_dic(path):
    pass_list = []
    try:
        file_ = open(path,'r')
        for password in file_:
            pass_list.append(password.strip())
        file_.close()
        return pass_list
    except:
        return '读取字典出错'
def get_ip_list(ip):
    ip_list = []
    iptonum = lambda x:sum([256**j*int(i) for j,i in enumerate(x.split('.')[::-1])])
    numtoip = lambda x: '.'.join([str(x/(256**i)%256) for i in range(3,-1,-1)])
    if '-' in ip:
        ip_range = ip.split('-')
        ip_start = long(iptonum(ip_range[0]))
        ip_end = long(iptonum(ip_range[1]))
        ip_count = ip_end - ip_start
        if ip_count >= 0 and ip_count <= 65536:
            for ip_num in range(ip_start,ip_end+1):
                ip_list.append(numtoip(ip_num))
        else:
            print '-h 格式错误'
    elif '.ini' in ip:
        ip_config = open(ip,'r')
        for ip in ip_config:
            ip_list.extend(get_ip_list(ip.strip()))
        ip_config.close()
    else:
        ip_split=ip.split('.')
        net = len(ip_split)
        if net == 2:
            for b in range(1,255):
                for c in range(1,255):
                    ip = "%s.%s.%d.%d"%(ip_split[0],ip_split[1],b,c)
                    ip_list.append(ip)
        elif net == 3:
            for c in range(1,255):
                ip = "%s.%s.%s.%d"%(ip_split[0],ip_split[1],ip_split[2],c)
                ip_list.append(ip)
        elif net ==4:
            ip_list.append(ip)
        else:
            print "-h 格式错误"
    return ip_list
def t_join(m_count):
    tmp_count = 0
    i = 0
    if I < m_count:
        count = len(ip_list) + 1
    else:
        count = m_count
    while True:
        time.sleep(4)
        ac_count = threading.activeCount()
        if ac_count < count  and ac_count == tmp_count:
            i+=1
        else:
            i=0
        tmp_count = ac_count
        if (queue.empty() and threading.activeCount() <= 1) or i > 5:
            break
def inLine(message):
        erase()
        sys.stdout.write(message)
        sys.stdout.flush()
def erase():
    if sys.platform in ["win32", "msys"]:
        csbi = GetConsoleScreenBufferInfo()
        line = "\b" * int(csbi.dwCursorPosition.X)
        sys.stdout.write(line)
        width = csbi.dwCursorPosition.X
        csbi.dwCursorPosition.X = 0
        FillConsoleOutputCharacter(STDOUT, " ", width, csbi.dwCursorPosition)
        sys.stdout.write(line)
        sys.stdout.flush()
    else:
        sys.stdout.write("\033[1K")
        sys.stdout.write("\033[0G")
#连接类
class Crack():
    def __init__(self,ip,port,server,timeout):
        self.ip = ip
        self.port = port
        self.server = server
        self.timeout = timeout
    def run(self):
        user_list = USER_DIC[self.server]
        for user in user_list:
            for pass_ in PASSWORD_DIC:
                pass_ = str(pass_.replace('{user}', user))
                k = getattr(self,self.server)
                result = k(user,pass_)
                if result:return result
    def ftp(self,user,pass_):
        linePrint().inLine('正在测试username:%s,password:%s' % (user,pass_))
        try:
            ftp=ftplib.FTP()
            ftp.connect(self.ip,self.port)
            ftp.login(user,pass_)
            if user == 'ftp':return "anonymous"
            return "username:%s,password:%s"%(user,pass_)
        except Exception,e:
            pass
    def mysql(self,user,pass_):
        inLine('正在测试username:%s,password:%s' % (user,pass_))
        sock = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        sock.connect((self.ip,int(self.port)))
        packet = sock.recv(254)
        plugin,scramble = self.get_scramble(packet)
        if not scramble:return 3
        auth_data = self.get_auth_data(user,pass_,scramble,plugin)
        sock.send(auth_data)
        result = sock.recv(1024)
        if result == "\x07\x00\x00\x02\x00\x00\x00\x02\x00\x00\x00":
            return "username:%s,password:%s" % (user,pass_)
    def postgresql(self,user,pass_):
        inLine('正在测试username:%s,password:%s' % (user,pass_))
        try:
            sock=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
            sock.connect((self.ip,int(self.port)))
            packet_length = len(user) + 7 +len("\x03user  database postgres application_name psql client_encoding UTF8  ")
            p="%c%c%c%c%c\x03%c%cuser%c%s%cdatabase%cpostgres%capplication_name%cpsql%cclient_encoding%cUTF8%c%c"%( 0,0,0,packet_length,0,0,0,0,user,0,0,0,0,0,0,0,0)
            sock.send(p)
            packet = sock.recv(1024)
            psql_salt=[]
            if packet[0]=='R':
                a=str([packet[4]])
                b=int(a[4:6],16)
                authentication_type=str([packet[8]])
                c=int(authentication_type[4:6],16)
                if c==5:psql_salt=packet[9:]
            else:return 3
            buf=[]
            salt = psql_salt
            lmd5= self.make_response(buf,user,pass_,salt)
            packet_length1=len(lmd5)+5+len('p')
            pp='p%c%c%c%c%s%c'%(0,0,0,packet_length1 - 1,lmd5,0)
            sock.send(pp)
            packet1 = sock.recv(1024)
            if packet1[0] == "R":
                return "username:%s,password:%s" % (user,pass_)
        except Exception,e:
            return 3
    def redis(self,user,pass_):
        inLine('正在测试username:%s,password:%s' % (user,pass_))
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.connect((self.ip,int(self.port)))
            s.send("INFO\r\n")
            result = s.recv(1024)
            if "redis_version" in result:
                return "unauthorized"
            elif "Authentication" in result:
                for pass_ in PASSWORD_DIC:
                    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    s.connect((self.ip,int(self.port)))
                    s.send("AUTH %s\r\n"%(pass_))
                    result = s.recv(1024)
                    if '+OK' in result:
                        return "username:%s,password:%s" % (user,pass_)
        except Exception,e:
            return 3
    def mssql(self,user,pass_):
        inLine('正在测试username:%s,password:%s' % (user,pass_))
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.connect((self.ip,self.port))
            hh=binascii.b2a_hex(self.ip)
            husername=binascii.b2a_hex(user)
            lusername=len(user)
            lpassword=len(pass_)
            ladd=len(self.ip)+len(str(self.port))+1
            hladd=hex(ladd).replace('0x','')
            hpwd=binascii.b2a_hex(pass_)
            pp=binascii.b2a_hex(str(self.port))
            address=hh+'3a'+pp
            hhost= binascii.b2a_hex(self.ip)
            data="0200020000000000123456789000000000000000000000000000000000000000000000000000ZZ5440000000000000000000000000000000000000000000000000000000000X3360000000000000000000000000000000000000000000000000000000000Y373933340000000000000000000000000000000000000000000000000000040301060a09010000000002000000000070796d7373716c000000000000000000000000000000000000000000000007123456789000000000000000000000000000000000000000000000000000ZZ3360000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000Y0402000044422d4c6962726172790a00000000000d1175735f656e676c69736800000000000000000000000000000201004c000000000000000000000a000000000000000000000000000069736f5f31000000000000000000000000000000000000000000000000000501353132000000030000000000000000"
            data1=data.replace(data[16:16+len(address)],address)
            data2=data1.replace(data1[78:78+len(husername)],husername)
            data3=data2.replace(data2[140:140+len(hpwd)],hpwd)
            if lusername>=16:
                data4=data3.replace('0X',str(hex(lusername)).replace('0x',''))
            else:
                data4=data3.replace('X',str(hex(lusername)).replace('0x',''))
            if lpassword>=16:
                data5=data4.replace('0Y',str(hex(lpassword)).replace('0x',''))
            else:
                data5=data4.replace('Y',str(hex(lpassword)).replace('0x',''))
            hladd = hex(ladd).replace('0x', '')
            data6=data5.replace('ZZ',str(hladd))
            data7=binascii.a2b_hex(data6)
            sock.send(data7)
            packet=sock.recv(1024)
            if 'master' in packet:
                return "username:%s,password:%s" % (user,pass_)
        except:
            return 3
    def mongodb(self,user,pass_):
        inLine('正在测试username:%s,password:%s' % (user,pass_))
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.connect((self.ip,int(self.port)))
            data = binascii.a2b_hex("3a000000a741000000000000d40700000000000061646d696e2e24636d640000000000ffffffff130000001069736d6173746572000100000000")
            s.send(data)
            result = s.recv(1024)
            if "ismaster" in result:
                getlog_data = binascii.a2b_hex("480000000200000000000000d40700000000000061646d696e2e24636d6400000000000100000021000000026765744c6f670010000000737461727475705761726e696e67730000")
                s.send(getlog_data)
                result = s.recv(1024)
                if "totalLinesWritten" in result:
                    return "unauthorized"
                else:return 3
        except Exception,e:
            return 3
    def memcached(self,user,pass_):
        inLine('正在测试username:%s,password:%s' % (user,pass_))
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((self.ip,int(self.port)))
        s.send("stats\r\n")
        result = s.recv(1024)
        if "version" in result:
            return "unauthorized"
    def elasticsearch(self,user,pass_):
        inLine('正在测试username:%s,password:%s' % (user,pass_))
        url = "http://"+self.ip+":"+str(self.port)+"/_cat"
        data = urllib2.urlopen(url).read()
        if '/_cat/master' in data:
            return "unauthorized"
        else:
            return 3
    def telnet(self,user,pass_):
        inLine('正在测试username:%s,password:%s' % (user,pass_))
        try:
            tn = telnetlib.Telnet(self.ip,self.port,self.timeout)
            time.sleep(0.5)
            os = tn.read_some()
        except Exception ,e:
            return 3
        user_match="(?i)(login|user|username)"
        pass_match='(?i)(password|pass)'
        login_match='#|\$|>'
        if re.search(user_match,os):
            try:
                tn.write(str(user)+'\r\n')
                tn.read_until(pass_match,timeout=2)
                tn.write(str(pass_)+'\r\n')
                login_info=tn.read_until(login_match,timeout=3)
                tn.close()
                if re.search(login_match,login_info):
                    return "username:%s,password:%s" % (user,pass_)
            except Exception,e:
                pass
        else:
            try:
                info=tn.read_until(user_match,timeout=2)
            except Exception,e:
                return 3
            if re.search(user_match,info):
                try:
                    tn.write(str(user)+'\r\n')
                    tn.read_until(pass_match,timeout=2)
                    tn.write(str(pass_)+'\r\n')
                    login_info=tn.read_until(login_match,timeout=3)
                    tn.close()
                    if re.search(login_match,login_info):
                        return "username:%s,password:%s" % (user,pass_)
                except Exception,e:
                    return 3
            elif re.search(pass_match,info):
                tn.read_until(pass_match,timeout=2)
                tn.write(str(pass_)+'\r\n')
                login_info=tn.read_until(login_match,timeout=3)
                tn.close()
                if re.search(login_match,login_info):
                    return "password:%s" % (pass_)
    def get_hash(self,password, scramble):
        hash_stage1 = hashlib.sha1(password).digest()
        hash_stage2 = hashlib.sha1(hash_stage1).digest()
        to = hashlib.sha1(scramble+hash_stage2).digest()
        reply = [ord(h1) ^ ord(h3) for (h1, h3) in zip(hash_stage1, to)]
        hash = struct.pack('20B', *reply)
        return hash
    def get_scramble(self,packet):
        scramble,plugin = '',''
        try:
            tmp = packet[15:]
            m = re.findall("\x00?([\x01-\x7F]{7,})\x00", tmp)
            if len(m)>3:del m[0]
            scramble = m[0] + m[1]
        except:
            return '',''
        try:
            plugin = m[2]
        except:
            pass
        return plugin,scramble
    def get_auth_data(self,user,password,scramble,plugin):
        user_hex = binascii.b2a_hex(user)
        pass_hex = binascii.b2a_hex(self.get_hash(password,scramble))
        data = "85a23f0000000040080000000000000000000000000000000000000000000000" + user_hex + "0014" + pass_hex
        if plugin:data+=binascii.b2a_hex(plugin)+ "0055035f6f73076f737831302e380c5f636c69656e745f6e616d65086c69626d7973716c045f7069640539323330360f5f636c69656e745f76657273696f6e06352e362e3231095f706c6174666f726d067838365f3634"
        len_hex = hex(len(data)/2).replace("0x","")
        auth_data = len_hex + "000001" +data
        return binascii.a2b_hex(auth_data)
    def make_response(self,buf,username,password,salt):
        pu=hashlib.md5(password+username).hexdigest()
        buf=hashlib.md5(pu+salt).hexdigest()
        return 'md5'+buf
    
#多线程类
class ThreadNum(threading.Thread):
    def __init__(self,queue):
        threading.Thread.__init__(self)
        self.queue = queue
    def run(self):
        while True:
            try:
                if queue.empty():break
                queue_task = self.queue.get()
            except:
                break
            try:
                task_type,task_host,task_port = queue_task.split(":")
                if task_type == 'portscan':
                    data = scan_port(task_host,task_port)
                    if data:
                        server_name = server_discern(task_host,task_port,data)
                        if server_name:
                            log('discern',task_host,task_port,server_name)
                            queue.put(":".join([server_name,task_host,task_port]))
                else:
                    result = pass_crack(task_type,task_host,task_port)
                    if result and result !=3:log(task_type,task_host,task_port,result)
            except Exception,e:
                continue
#主函数
if __name__=="__main__":
    msg = '''
______ _    _        _____                     _    
|  ___| |  | |      /  ___|                   | |   
| |_  | |  | |______\ `--.  ___ _ __ __ _  ___| | __
|  _| | |/\| |______|`--. \/ __| '__/ _` |/ __| |/ /
| |   \  /\  /      /\__/ / (__| | | (_| | (__|   < 
\_|    \/  \/       \____/ \___|_|  \__,_|\___|_|\_\ 
                                                    
Usage: python FW-Scrack.py -h 0.0.0.0 [-p 21,80,3306] [-m 50] [-t 10] [-d pass.txt] [-n]
    '''
    if len(sys.argv) < 2:
        print msg
    try:
        options,args = getopt.getopt(sys.argv[1:],"h:p:m:t:d:n")
        ip = ''
        port = '21,23,1433,3306,5432,6379,9200,11211,27017'
        m_count = 100
        for opt,arg in options:
            if opt == '-h':
                ip = arg
            elif opt == '-p':
                port = arg
            elif opt == '-m':
                m_count = int(arg)
            elif opt == '-t':
                TIMEOUT = int(arg)
            elif opt == '-d':
                PASSWORD_DIC = get_password_dic(arg)
        socket.setdefaulttimeout(TIMEOUT)
        if ip:
            ip_list = get_ip_list(ip)
            port_list = port.split(',')
            for ip_str in ip_list:
                for port_int in port_list:
                    I+=1
                    queue.put(':'.join(['portscan',ip_str,port_int]))
            for i in range(m_count):
                t = ThreadNum(queue)
                t.setDaemon(True)
                t.start()
            t_join(m_count)
    except Exception,e:
        print msg
    finally:
        print "\033[0;35m\t\nTask Completed\033[0m"
