from IMClient.IMClientProtocol import *
from IMClient.IMClientSocket import IMClientSocket
from IMClient.clientAuthorize import *
from IMClient.clientAuthorize import md5Calc


class loginError(Exception):
    def __init__(self):
        pass


class userHandle():
    def __init__(self):
        self.user = IMClientSocket()
        self.userID = None
        self.isLogin = False
        self.friendList = dict()

    def login(self, userID, password):
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
        #self.friendList.update(msg['content']['msg']['friendList'])
        return msg['content']['msg']['friendList']

    def userRegister(self, userID, password):
        userID = int(userID)
        msg = self.user.send(
            clientProtocol.info,
            userID,
            {'infoProtocol': infoProtocol.userRegister.value, 'userID': userID, 'password': md5Calc(password)}
        )
        return msg['content']['msg']

    def __repr__(self):
        return '<User: {} isLogin: {}'.format(self.userID, self.isLogin)
