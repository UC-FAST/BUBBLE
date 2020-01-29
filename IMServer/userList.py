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
        logger.info('User {} Added.'.format(userID))

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
                except Exception as e:
                    logger.warning('{}'.format(e))

    def update(self, userID):
        if userID in self.userList_.keys():
            self.userList_[userID] = int(time())
            logger.info('{} GOT a New Life'.format(userID))

    @property
    def userList(self):
        return list(self.userList_.keys())

    def isOnline(self, userIDList):
        result = list()
        for _ in userIDList.keys():
            result.append({'userID': _, 'name': userIDList[_], 'isOnline': int(_) in self.userList_})
        return result

    def __contains__(self, userID):
        return userID in self.userList_.keys()
