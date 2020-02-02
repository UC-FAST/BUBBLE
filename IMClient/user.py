import sqlite3
import base64
import threading
from os.path import exists
import prettytable as pt
from IMClient.IMClientProtocol import *
from IMClient.IMClientSocket import IMClientSocket
from IMClient.clientAuthorize import md5Calc, getLocalTime


class loginError(Exception):
    def __init__(self):
        pass


class userHandle():
    def __init__(self, address, port):
        self.userSocket = IMClientSocket(address, port)
        self.userID = None
        self.isLogin = False
        self.friendList = set()

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
                cursor.execute(
                    'CREATE TABLE message(time REAL,fromUser INTEGER,msg,type INTEGER,fileName,isShown INTEGER DEFAULT 0)')
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
            self.friendList.add(_['userID'])
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
        if self.__storageMsg(msg['content']['msg']):
            return self.delServerMsg()

    def delServerMsg(self):
        state = self.userSocket.send(clientProtocol.info, self.userID, {'infoProtocol': infoProtocol.delMsg.value})
        return state['content']['msg']['state']

    def __storageMsg(self, msg):
        db = sqlite3.connect('{}.db'.format(self.userID))
        cursor = db.cursor()
        for timeStamp in msg.keys():
            for msgGroup in msg[timeStamp]:
                cursor.execute('INSERT INTO message(time, fromUser, msg, type,fileName) VALUES (?,?,?,?,?)',
                               (timeStamp, msgGroup['fromUser'], msgGroup['msg'], msgGroup['type'],
                                msgGroup['fileName']))
        cursor.close()
        db.commit()
        db.close()
        return True

    def sendMsg(self, toUser, msg):
        msg = self.userSocket.send(clientProtocol.text, self.userID,
                                   {'content': base64.b64encode(msg.encode()).decode(), 'toUser': toUser})
        return msg

    def sendPicture(self, toUser, filename):
        with open(filename, 'rb') as f:
            file = f.read()
        msg = self.userSocket.send(clientProtocol.pict, self.userID, {
            'fileName': '{}-{}'.format(self.userID, filename),
            'content': base64.b64encode(file).decode(),
            'toUser': toUser
        })
        return msg

    def sendFile(self, toUser, filename):
        with open(filename, 'rb') as f:
            file = f.read()
        msg = self.userSocket.send(clientProtocol.file, self.userID, {
            'fileName': '{}-{}'.format(self.userID, filename),
            'content': base64.b64encode(file).decode(),
            'toUser': toUser
        })
        return msg

    def sendVoice(self, toUser, filename):
        with open(filename, 'rb') as f:
            file = f.read()
        msg = self.userSocket.send(clientProtocol.voice, self.userID, {
            'fileName': '{}-{}'.format(self.userID, filename),
            'content': base64.b64encode(file).decode(),
            'toUser': toUser
        })
        return msg

    def getServerTips(self):
        a = self.userSocket.send(clientProtocol.info, -1, {'infoProtocol': infoProtocol.serverTips.value})
        return a['content']['msg']['announcement'], a['content']['msg']['maxim']

    def hasFriend(self, ID):
        return ID in self.friendList

    def showFriendRequest(self):
        self.getNewMsg()
        db = sqlite3.connect('{}.db'.format(self.userID))
        cursor = db.cursor()
        cursor.execute('SELECT time,fromUser From message WHERE type=0')
        result = cursor.fetchone()
        while result:
            time, fromUser = result
            choice = input(
                'AT {} {} Sent a Friend Request To You,Accept?(Y/N)'.format(getLocalTime(time), fromUser)
            )
            if choice == 'Y' or choice == 'y':
                self.userSocket.send(
                    clientProtocol.info, self.userID,
                    {'infoProtocol': infoProtocol.addFriend.value, 'fromUser': fromUser}
                )
            cursor.execute('DELETE FROM message WHERE type=0 AND fromUser=?', (fromUser,))
            result = cursor.fetchone()
        cursor.close()
        db.commit()
        db.close()
        self.getFriendList()

    def recallMsg(self, fromUser, time=3):
        self.getNewMsg()
        fromUser = int(fromUser)
        db = sqlite3.connect('{}.db'.format(self.userID))
        cursor = db.cursor()
        cursor.execute(
            'SELECT time, fromUser, msg, fileName ,type FROM message WHERE type !=0 and fromUser=? and isShown=0',
            (fromUser,))
        msgGroup = cursor.fetchone()
        while msgGroup:
            timeStamp, fromUser, msg, fileName, msgType = msgGroup
            if msgType == clientProtocol.text.value:
                print('{}      {}'.format(getLocalTime(timeStamp), base64.b64decode(msg.encode()).decode()))
                cursor.execute(
                    'UPDATE message SET isShown=1 WHERE time=? AND fromUser=? AND msg=? AND type=?',
                    (timeStamp, fromUser, msg, msgType))
                db.commit()
            if msgType == clientProtocol.pict.value:
                print('{}      收到图片 {}'.format(getLocalTime(timeStamp), fileName))
                with open(fileName, 'rw')as f:
                    f.write(base64.b64decode(msg.encode()))
            if msgType == clientProtocol.voice.value:
                print('{}      收到一条语言消息 {}'.format(getLocalTime(timeStamp), fileName))
                with open(fileName, 'rw')as f:
                    f.write(base64.b64decode(msg.encode()))
            if msgType == clientProtocol.file.value:
                print('{}      收到文件 {}'.format(getLocalTime(timeStamp), fileName))
                with open(fileName, 'rw')as f:
                    f.write(base64.b64decode(msg.encode()))
            msgGroup = cursor.fetchone()
        cursor.close()
        db.commit()
        db.close()
        threading.Timer(time, self.recallMsg, args=(fromUser, time)).start()

    def addFriend(self, toUser):
        toUser = int(toUser)
        self.userSocket.send(clientProtocol.info, self.userID,
                             {'infoProtocol': infoProtocol.friendRequest.value, 'toUser': toUser})

    def changePassword(self, oldPwd, newPwd):
        return self.userSocket.send(clientProtocol.info, self.userID,
                                    {'infoProtocol': infoProtocol.changePassword.value, 'oldPwd': md5Calc(oldPwd),
                                     'newPwd': md5Calc(newPwd)
                                     }
                                    )['content']['msg']['state']
