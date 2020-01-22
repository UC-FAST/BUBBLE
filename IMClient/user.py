from IMClient.IMClientProtocol import *
from IMClient.IMClientSocket import IMClientSocket
from IMClient.clientAuthorize import *


class loginError(Exception):
    def __init__(self):
        pass


class userHandle():
    def __init__(self):
        self.user = IMClientSocket()
        self.userID = None
        self.isLogin = False
        self.friendList = set()

    def login(self, userID, password):
        userID = str(userID)
        msg = self.user.send(clientProtocol.login, userID, {'userID': userID, 'password': md5Calc(password)})
        if msg['content']['protocol'] == clientProtocol.reinfo.value:
            if msg['content']['msg']['infoProtocol'] == infoProtocol.invaildMessage.value:
                return
        if msg['content']['msg']['login']:
            self.userID = userID
            self.isLogin = True
            return self.isLogin
        else:
            raise loginError

    def getFriendList(self):
        msg = self.user.send(clientProtocol.info, self.userID, {'infoProtocol': infoProtocol.friendList.value})
        for _ in msg['content']['msg']['friendList']:
            self.friendList.add(_)
        return self.friendList

    def __repr__(self):
        return '<User: {} isLogin: {}'.format(self.userID, self.isLogin)
