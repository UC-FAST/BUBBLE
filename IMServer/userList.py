from time import time
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class userList():
    def __init__(self, timeout=60):
        self.userList_ = dict()
        self.timeout = timeout

    def addUser(self, userID):
        self.userList_[userID] = int(time())
        logger.info('User {} added.'.format(userID))

    def delUser(self, userID):
        return self.userList_.pop(userID)

    def cleanUp(self):
        now = int(time())
        keys = list(self.userList_.keys())
        for index in keys:
            if now - self.userList_[index] > self.timeout:
                try:
                    self.delUser(index)
                    logger.info('User {} Screamed Ahhhhh!'.format(index))
                except RuntimeError:
                    pass
        print(self.userList)

    def update(self, userID):
        self.userList_[userID] = int(time())

    @property
    def userList(self):
        return list(self.userList_.keys())

    def __contains__(self, userID):
        return userID in self.userList_.keys()
