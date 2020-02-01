import threading
import requests
import prettytable as pt
from . import user


def version():
    return 'v0.0.1'


def updateChecker():
    url = 'https://microfish.club/bubble/update.json'
    r = requests.get(url).json()
    if not version() == r['version']:
        print('检测到新版本，正在下载更新')
        r = requests.get('https://microfish.club/bubble/bubble.zip')


def welcome():
    print('Bubble {}'.format(version()))
    updateChecker()


def showStartUpMenu():
    tb = pt.PrettyTable()
    tb.header = False
    tb.junction_char = '-'
    print('Start Up Menu')
    tb.add_row([1, 'login'])
    tb.add_row([2, 'register'])
    tb.add_row([3, 'exit'])
    print(tb)


def showMainMenu():
    tb = pt.PrettyTable()
    tb.header = False
    tb.junction_char = '-'
    print('Main Menu')
    tb.add_row([1, 'chat'])
    tb.add_row([2, 'friend system'])
    tb.add_row([3, 'personal set up'])
    print(tb)


def showMenu(row, header=False, junctionChar='-'):
    tb = pt.PrettyTable()
    if header:
        tb.field_names = header
    else:
        tb.header = False
    tb.junction_char = junctionChar
    for _ in row:
        tb.add_row(_)
    print(tb)


def register(socket: user.userHandle):
    userID = input('User ID: ')
    pwd = input('Password: ')
    msg = socket.userRegister(userID, pwd)
    print(msg)


def mainFunc(socket: user.userHandle):
    userID = int(input('User ID: '))
    pwd = input('Password: ')
    socket.login(userID, pwd)
    print('Login Successfully')
    while True:
        showMainMenu()
        choice = input('>')
        if choice == '1':
            chatSystem(socket)
        elif choice == '2':
            friendSystem(socket)
        elif choice == '3':
            friendSystem(socket)


def chatSystem(socket: user.userHandle):
    print(socket.getFriendList())
    friendID = int(input('Input Friend ID :'))
    threading.Timer(3, socket.recallMsg, args=(friendID, 3)).start()
    print('chat with {}'.format(friendID))
    while True:
        showMenu((['1', '发送文字'], ['2', '发送图片'], ['3', '发送文件'], ['4', '发送语音']))
        choice = input('>')
        if choice == '1':
            msg = input('输入消息 ：')
            socket.sendMsg(friendID, msg)
        elif choice == '3':
            msg = input('输入文件名：')
            socket.sendFile(friendID, msg)
        else:
            print('暂未开放')


def friendSystem(socket: user.userHandle):
    print(socket.getFriendList())
    while True:
        showMenu((['1', 'addUser'], ['2', 'checkFriendRequest'], ['3', 'friendList'], ['4', 'return']))
        choice = input('>')
        if choice == '1':
            friendID = input("Input Your Friend's ID: ")
            socket.addFriend(friendID)
        if choice == '2':
            socket.showFriendRequest()
        if choice == '3':
            print(socket.getFriendList())
        if choice == '4':
            return


def personalSetUpSystem(socket: user.userHandle):
    pass


def showSetUpMenu():
    pass
