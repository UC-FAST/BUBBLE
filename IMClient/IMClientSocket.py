import time
import socket
import json
from IMClient.IMClientProtocol import *
from IMClient.clientAuthorize import md5Calc


class jsonEncoding(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, Enum):
            return o.value


class IMClientSocket:
    def __init__(self, address='127.0.0.1', port=8760):
        self.__address = address
        self.__port = port

    def __sendmsg(self, *msg):
        self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self._socket.bind(('127.0.0.1', 5280))
        self._socket.connect((self.__address, self.__port))
        recv = None
        for i in msg:
            self._socket.sendall(i)  # 第一次发送数据包长度消息，第二次发送数据包
            recv = self._socket.recv(1024).decode('UTF-8')  # 第一次接收服务器占位消息，第二次接收服务器数据包长度消息
        self._socket.sendall(b'OK')  # 占位消息
        recv = json.loads(recv)
        msg = self._socket.recv(recv['content']['msg']['length'])
        # self._socket.shutdown(socket.SHUT_RDWR)
        return msg

    def send(self, protocol, userID, msg):
        """对socket.send的简单封装"""
        content = dict()
        content['msg'] = msg
        content['userID'] = int(userID)
        content['protocol'] = protocol.value
        content['time'] = time.time()
        package = {'content': content, 'hash': md5Calc(content)}
        package = json.dumps(package, cls=jsonEncoding)
        '''**********数据包长度计算**********'''
        length = len(package)
        lengthInfo = {
            'msg': {
                'infoProtocol': infoProtocol.contentLength.value,
                'length': length
            },
            "userID": userID,
            "time": time.time(),
            "protocol": clientProtocol.info.value
        }
        packageLength = json.dumps({'content': lengthInfo, 'hash': md5Calc(lengthInfo)})
        return json.loads(self.__sendmsg(packageLength.encode(), package.encode()))
