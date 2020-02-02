import socket
import sqlite3
import time
import logging
import threading
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
            cursor.execute(
                'CREATE TABLE userMsg(toUser INTEGER,fromUser INTEGER,time REAL,msg,type INTEGER,fileName default NULL)')
            cursor.close()
            db.commit()
            db.close()
        self.userList = userList.userList()
        self.__address = address
        self.__port = port
        self._socket = socket.socket()
        self._socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self._socket.bind((self.__address, self.__port))

    def userListCleanup(self):
        self.userList.cleanUp()
        t = threading.Timer(60, self.userListCleanup)
        t.start()

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
        # {'content': {'msg': {'infoProtocol': 5}, 'userID': -1, 'protocol': 6, 'time': 1580475048.316727},'hash': 'b71e4997224519dcc4466858ce3bfe7a'}
        if not msg:
            return None
        msg = json.loads(msg)
        logging.info('Message From {} Protocol {}'.format(msg['content']['userID'], msg['content']['protocol']))
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
                    text['msg'] = {'announcement': 'BUBBLE内测上线.',
                                   'maxim': 'Across the Great Wall we can reach every corner in the world.'}
                elif info == infoProtocol.delMsg.value:
                    msgHandle.delMessage(msg['userID'])
                    text['msg'] = {'state': True}
                elif info == infoProtocol.addFriend.value:
                    msgHandle.addFriend(msg['userID'], msg['msg']['fromUser'])
                    msgHandle.addFriend(msg['msg']['fromUser'], msg['userID'])
                    text['msg'] = {'state': True}
                elif info == infoProtocol.friendRequest.value:
                    msgHandle.storageMsg(msg['userID'], msg['msg']['toUser'], msg['time'], msg=None, type=0,
                                         fileName=None)
                    text['msg'] = {'state': True}
                elif info == infoProtocol.changePassword.value:
                    text['msg'] = {
                        'state': msgHandle.changePassword(msg['userID'], msg['msg']['oldPwd'], msg['msg']['newPwd'])}
                text['protocol'] = serverProtocol.reinfo
            elif protocol == serverProtocol.enquire.value:
                text['msg'] = msgHandle.getNewMsg(msg['userID'])
                text['protocol'] = serverProtocol.reenquire
            elif protocol == serverProtocol.pict.value:
                msgHandle.storageMsg(msg['userID'], msg['msg']['toUser'], msg['time'], msg['msg']['content'],
                                     serverProtocol.pict.value, msg['msg']['fileName'])
                text['msg'] = True
                text['protocol'] = serverProtocol.repict.value
            elif protocol == serverProtocol.file.value:
                pass
            elif protocol == serverProtocol.voice.value:
                pass
            elif protocol == serverProtocol.text.value:
                msgHandle.storageMsg(msg['userID'], msg['msg']['toUser'], msg['time'], msg['msg']['content'],
                                     serverProtocol.text.value, None)
                text['msg'] = True
                text['protocol'] = serverProtocol.retext.value
            elif protocol:
                pass


        else:
            text['msg'] = {'infoProtocol': infoProtocol.invaildMessage}
            text['protocol'] = serverProtocol.reinfo
        text['user'] = 0  # 服务器ID为0
        text['time'] = time.time()
        text = packUp(text)
        # logging.info('Return {}'.format(str(text)))
        return dumps(text)
