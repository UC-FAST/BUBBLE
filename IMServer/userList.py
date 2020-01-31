from time import time
import logging
import threading
from .msgHandle import getUserInfo

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class userList():
    def __init__(self, timeout=60):
        self._userList_ = dict()
        self.timeout = timeout
        self.__lock = threading.Lock()

    def addUser(self, userID):
        with self.__lock:
            self._userList_[userID] = int(time())
        logger.info('User {} Added.'.format(userID))

    def delUser(self, userID):
        with self.__lock:
            return self._userList_.pop(userID)

    def cleanUp(self):
        with self.__lock:
            now = int(time())
            keys = list(self._userList_.keys())
            for index in keys:
                if now - self._userList_[index] > self.timeout:
                    try:
                        self.delUser(index)
                        logger.info('The Server Killed {}, User {} Screamed Ahhhhh!'.format(index, index))
                        if len(self._userList_.keys()) == 0:
                            logger.info('So No One is Online Now.')
                        else:
                            logger.info("We have {} User(s) Online".format(len(self._userList_.keys())))
                    except Exception as e:
                        logger.warning('{}'.format(e))

    def update(self, userID):
        with self.__lock:
            if userID in self._userList_.keys():
                self._userList_[userID] = int(time())
                logger.info('{} GOT a New Life'.format(userID))

    @property
    def userList(self):
        return list(self._userList_.keys())

    def isOnline(self, userIDList):
        result = list()
        for _ in userIDList:
            result.append({'userID': _, 'name': getUserInfo(_)[1], 'isOnline': int(_) in self._userList_})
        return result

    def __contains__(self, userID):
        return userID in self._userList_.keys()

    def __len__(self):
        return len(self._userList_.keys())
