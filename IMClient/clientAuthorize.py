import hashlib
import time


def md5Calc(msg):
    msg = str(msg)
    md5 = hashlib.md5()
    md5.update(msg.encode())
    return md5.hexdigest()


def getLocalTime(timeStamp):
    timeStamp=float(timeStamp)
    return time.asctime(time.localtime(timeStamp))
