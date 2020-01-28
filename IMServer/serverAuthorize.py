import hashlib
import json
from enum import Enum


class jsonEncoding(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, Enum):
            return o.value


def md5Calc(msg):
    '''摘要算法，服务器端与客户端代码应保持一致'''
    msg = str(msg)
    md5 = hashlib.md5()
    md5.update(msg.encode())
    return md5.hexdigest()


def packUp(msg):
    '''计算数据包校验和'''
    return {'content': msg, 'hash': md5Calc(msg)}


def dumps(msg):
    return json.dumps(msg, cls=jsonEncoding)


def isVaildData(msg):
    '''数据包合法性校验'''
    hash = msg['hash']
    return hash == md5Calc(str(msg['content']))
