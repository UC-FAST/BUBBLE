from time import time


class userList():
    def __init__(self, timeout=60):
        self.userList_ = dict()
        self.timeout = timeout

    def addUser(self, userID):
        self.userList_[userID] = int(time())

    def delUser(self, userID):
        return self.userList_.pop(userID)

    def cleanUp(self):
        now = int(time())
        for index in self.userList_.keys():
            if now - self.userList_[index] > self.timeout:
                self.delUser(index)

    def update(self, userID):
        self.userList_[userID] = int(time())

    @property
    def userList(self):
        return list(self.userList_.keys())

    def __contains__(self, userID):
        return userID in self.userList_.keys()
