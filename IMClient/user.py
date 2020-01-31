import sqlite3
import base64
from os.path import exists
from os.path import splitext
import prettytable as pt
from IMClient.IMClientProtocol import *
from IMClient.IMClientSocket import IMClientSocket
from IMClient.clientAuthorize import md5Calc


class loginError(Exception):
    def __init__(self):
        pass


class userHandle():
    def __init__(self):
        self.userSocket = IMClientSocket()
        self.userID = None
        self.isLogin = False
        self.friendList = dict()

    def login(self, userID, password):
        userID = int(userID)
        msg = self.userSocket.send(clientProtocol.login, userID, {'userID': userID, 'password': md5Calc(password)})
        if msg['content']['protocol'] == clientProtocol.reinfo.value:
            if msg['content']['msg']['infoProtocol'] == infoProtocol.invaildMessage.value:
                return
        if msg['content']['msg']['login']:  # 登录成功
            self.userID = userID
            self.isLogin = True
            if not exists('{}.db'.format(self.userID)):
                db = sqlite3.connect('{}.db'.format(self.userID))
                cursor = db.cursor()
                cursor.execute('CREATE TABLE message(time,fromUser,msg,type)')
                cursor.close()
                db.commit()
                db.close()
            return self.isLogin
        else:
            raise loginError

    def getFriendList(self):
        msg = self.userSocket.send(clientProtocol.info, self.userID, {'infoProtocol': infoProtocol.friendList.value})
        tb = pt.PrettyTable()
        tb.junction_char = '-'
        print('Friend List')
        tb.field_names = ['No.', 'ID', 'Name', 'isOnline']
        for index, _ in enumerate(msg['content']['msg']['friendList'], start=1):
            tb.add_row([index, _['userID'], _['name'], _['isOnline']])
        return tb

    def userRegister(self, userID, password):
        userID = int(userID)
        msg = self.userSocket.send(
            clientProtocol.info,
            userID,
            {'infoProtocol': infoProtocol.userRegister.value, 'userID': userID, 'password': md5Calc(password)}
        )
        return msg['content']['msg']

    def __repr__(self):
        return '<User: {} isLogin: {}'.format(self.userID, self.isLogin)

    def getNewMsg(self):
        msg = self.userSocket.send(clientProtocol.enquire, self.userID, None)
        if self.storageMsg(msg['content']['msg']):
            return self.delServerMsg()

    def delServerMsg(self):
        state = self.userSocket.send(clientProtocol.info, self.userID, {'infoProtocol': infoProtocol.delMsg.value})
        return state['content']['msg']['state']

    def storageMsg(self, msg):
        db = sqlite3.connect('{}.db'.format(self.userID))
        cursor = db.cursor()
        for timeStamp in msg.keys():
            for msgGroup in msg[timeStamp]:
                cursor.execute('INSERT INTO message(time, fromUser, msg, type) VALUES (?,?,?,?)',
                               (timeStamp, msgGroup['fromUser'], msgGroup['msg'], msgGroup['type']))
        cursor.close()
        db.commit()
        db.close()
        return True

    def sendMsg(self, msg):
        msg = self.userSocket.send(clientProtocol.text, self.userID, {'msg': msg})
        return msg

    def sendPicture(self, filename):
        with open(filename, 'rb') as f:
            file = f.read()
        msg = self.userSocket.send(clientProtocol.pict, self.userID, {
            'format': splitext(filename)[1][1:],
            'fileName': '{}-{}'.format(self.userID, filename),
            'pict': base64.b64encode(file).decode()})
        return msg

    def sendFile(self, filename):
        with open(filename, 'rb') as f:
            file = f.read()
        msg = self.userSocket.send(clientProtocol.file, self.userID, {
            'format': splitext(filename)[1][1:],
            'fileName': '{}-{}'.format(self.userID, filename),
            'file': base64.b64encode(file).decode()})
        return msg

    def sendVoice(self, filename):
        with open(filename, 'rb') as f:
            file = f.read()
        msg = self.userSocket.send(clientProtocol.voice, self.userID, {
            'format': splitext(filename)[1][1:],
            'fileName': '{}-{}'.format(self.userID, filename),
            'file': base64.b64encode(file).decode()})
        return msg

    def getServerTips(self):
        a = self.userSocket.send(clientProtocol.info, -1, {'infoProtocol': infoProtocol.serverTips.value})
        return a['content']['msg']['announcement'], a['content']['msg']['maxim']
