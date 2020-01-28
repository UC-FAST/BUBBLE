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
            cursor.execute('CREATE TABLE userMSG(toUser PRIMARY KEY NOT NULL ,msg,fromUser,time)')
            cursor.execute(
                'INSERT INTO  userAuthorize (id, password) VALUES (872702913,"3b2fce04224301f9db63a5443bc02869")')
            cursor.execute(
                'INSERT INTO  userInfo (id, name, sex, friends) VALUES (872702913,"yang",0,"123,456")')
            cursor.close()
            db.commit()
            db.close()
        self.userList = userList.userList()
        self.__address = address
        self.__port = port
        self._socket = socket.socket()
        self._socket.bind((self.__address, self.__port))

    def mainLoop(self):
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
            msg = msgHandle.handle(skt.recv(contentLength).decode('UTF-8')).encode()

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
