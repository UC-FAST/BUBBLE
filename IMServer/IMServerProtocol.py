from enum import Enum


class serverProtocol(Enum):
    login = 0  # 登录
    enquire = 1  # 轮询
    text = 2  # 文本消息
    voice = 3  # 语音消息
    pict = 4  # 图片消息
    file = 5  # 文件
    info = 6  # 服务器端消息
    heartbeat = 7  # 维持心跳
    relogin = 8  # 登录
    reenquire = 9  # 轮询
    retext = 10  # 文本消息
    revoice = 11  # 语音消息
    repict = 12  # 图片消息
    refile = 13  # 文件
    reinfo = 14  # 服务器端消息
    reheartbeat = 15  # 维持心跳
    


class infoProtocol(Enum):
    invaildMessage = 0
    contentLength=1
    friendList = 2
    addFriend=3
