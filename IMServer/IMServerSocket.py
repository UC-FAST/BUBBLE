import socket
import json
import time
import logging

from IMServer.IMServerProtocol import *
from IMServer.serverAuthorize import *
from . import server

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class IMServerSocket():
    def __init__(self, address, port):
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

    def loginAuthorize(self, msg):
        '''账号密码数据校验'''
        with open('./IMServer/authorize.json') as f:
            content = json.load(f)
        try:
            return content[str(msg['userID'])] == msg['password']
        except KeyError:
            return False

    def handle(self, msg):
        if not msg:
            return None
        logging.info('Message {}'.format(msg))
        msg = json.loads(msg)
        text = dict()
        if isVaildData(msg):  # 数据合法性校验
            msg = msg['content']
            protocol = msg['protocol']
            if protocol == serverProtocol.login.value:  # 登录
                text['msg'] = {'login': self.loginAuthorize(msg['msg'])}
                text['protocol'] = serverProtocol.relogin
            elif protocol == serverProtocol.info.value:
                if msg['msg']['infoProtocol'] == infoProtocol.friendList.value:
                    text['msg'] = {'friendList': server.getFrendList(msg['userID'])}

                text['protocol'] = serverProtocol.reinfo
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
