import socket
import sqlite3
import time
import logging
from os.path import exists
from IMServer.IMServerProtocol import *
from IMServer.serverAuthorize import *
from . import userList
from . import msgHandle

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class IMServerSocket():
    def __init__(self, address, port):
        if not exists('IMServerUser.db'):
            db = sqlite3.connect('IMServerUser.db')
            cursor = db.cursor()
            cursor.execute('CREATE TABLE userAuthorize(id PRIMARY KEY NOT NULL ,password TEXT(32))')
            cursor.execute('CREATE TABLE userInfo(id PRIMARY KEY NOT NULL ,name,sex INTEGER,friends)')
            cursor.execute('CREATE TABLE userMsg(toUser ,fromUser,time,msg,type)')
            cursor.close()
            db.commit()
            db.close()
            msgHandle.register(872702913, "3b2fce04224301f9db63a5443bc02869")
            msgHandle.register(12, "121212")
            msgHandle.addFriend(872702913, 12)
            msgHandle.storageMsg(12, 872702913, 1213, 'wewe')
        self.userList = userList.userList()
        self.__address = address
        self.__port = port
        self._socket = socket.socket()
        self._socket.bind((self.__address, self.__port))

    def userListCleanup(self):
        while True:
            time.sleep(30)
            self.userList.cleanUp()
            time.sleep(30)

    def mainLoop(self):
        """服务器套接字接收的主循环"""
        """我已经尽量将注释写清楚了，但仍然不建议修改代码"""
        """这是座屎山"""
        self._socket.listen(5)
        logging.info('Listening {} on Port {}'.format(self.__address, self.__port))
        while True:
            skt, addr = self._socket.accept()
            logging.info(str(skt))
            """**********从客户端获取下一条数据的长度**********"""
            lengthInfo = json.loads(skt.recv(1024).decode('UTF-8'))
            contentLength = None
            if lengthInfo['content']['protocol'] == serverProtocol.info.value and \
                    lengthInfo['content']['msg']['infoProtocol'] == infoProtocol.contentLength.value:
                contentLength = lengthInfo['content']['msg']['length']
            skt.sendall('OK'.encode())  # 占位消息
            """**********处理数据**********"""
            msg = self.handle(skt.recv(contentLength).decode('UTF-8')).encode()

            '''**********服务器数据包长度计算**********'''
            length = len(msg)
            lengthInfo = {
                'msg': {
                    'infoProtocol': infoProtocol.contentLength.value,
                    'length': length
                },
                "userID": 0,
                "time": time.time(),
                "protocol": serverProtocol.reinfo.value
            }
            packageLength = json.dumps({'content': lengthInfo, 'hash': md5Calc(lengthInfo)})
            skt.sendall(packageLength.encode())  # 发送数据长度消息
            skt.recv(1024)  # 接收占位消息
            skt.sendall(msg)
            skt.close()

    def handle(self, msg):
        if not msg:
            return None
        logging.info('Message {}'.format(msg))
        msg = json.loads(msg)
        text = dict()
        if isVaildData(msg):  # 数据合法性校验
            msg = msg['content']
            protocol = msg['protocol']
            self.userList.update(msg['userID'])
            if protocol == serverProtocol.login.value:  # 登录
                state = msgHandle.loginAuthorize(msg['msg']['userID'], msg['msg']['password'])
                text['msg'] = {'login': state}
                text['protocol'] = serverProtocol.relogin
                if state:
                    self.userList.addUser(msg['msg']['userID'])
            elif protocol == serverProtocol.info.value:
                info = msg['msg']['infoProtocol']
                if info == infoProtocol.friendList.value:
                    result = self.userList.isOnline(msgHandle.getFriendList(msg['userID']))
                    text['msg'] = {'friendList': result}
                elif info == infoProtocol.userRegister.value:
                    text['msg'] = msgHandle.register(msg['msg']['userID'], msg['msg']['password'])
                elif info == infoProtocol.serverTips.value:
                    text['msg'] = {'announcement': 'nihao', 'maxim': 'qw'}
                elif info == infoProtocol.delMsg.value:
                    msgHandle.delMessage(msg['userID'])
                    text['msg'] = {'state': True}

                text['protocol'] = serverProtocol.reinfo
            elif protocol == serverProtocol.enquire.value:
                text['msg'] = msgHandle.getNewMsg(msg['userID'])
                text['protocol'] = serverProtocol.reenquire
            elif protocol:
                pass

            text['user'] = 0  # 服务器ID为0
            text['time'] = time.time()
        else:
            text['msg'] = {'infoProtocol': infoProtocol.invaildMessage}
            text['protocol'] = serverProtocol.reinfo
        text = packUp(text)
        logging.info('Return {}'.format(str(text)))
        return dumps(text)
