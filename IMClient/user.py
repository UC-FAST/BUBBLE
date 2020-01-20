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

    def login(self, userID, password):
        msg = self.user.send(clientProtocol.login, userID, {'userID': userID, 'password': md5Calc(password)})
        if msg['content']['protocol'] == clientProtocol.reinfo.value:
            if msg['content']['msg']['infoProtocol'] == infoProtocol.invaildMessage.value:
                pass
        if msg['content']['msg']['login']:
            self.userID = msg['content']['user']
            self.isLogin = True
            return self.isLogin
        else:
            raise loginError

    def userList(self):
        self.user.send(clientProtocol.info, self.userID, {'infoProtocol': infoProtocol.friendList.value})

    def __repr__(self):
        return '<User: {} isLogin: {}'.format(self.userID, self.isLogin)
