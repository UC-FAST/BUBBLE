import threading
import requests
import json
import os
import sys
import time
import prettytable as pt
from . import user

ver = 'v0.0.2'


def version():
    return ver


def updateChecker():
    url = 'https://microfish.club/bubble/update.json'
    r = requests.get(url).json()
    if version() != r['version']:
        print('检测到新版本，正在下载更新')
        if os.name == 'nt':
            downloadFile('bubble_{}.exe'.format(r['version']),
                         'https://{}/bubble/bubble_{}.exe'.format(readConfigFile()['server_address'], r['version']))
            os.system('bubble_{}.exe'.format(r['version']))
            sys.exit(0)


def downloadFile(name, url):
    headers = {'Proxy-Connection': 'keep-alive'}
    r = requests.get(url, stream=True, headers=headers)
    length = float(r.headers['content-length'])
    f = open(name, 'wb')
    count = 0
    count_tmp = 0
    time1 = time.time()
    for chunk in r.iter_content(chunk_size=512):
        if chunk:
            f.write(chunk)
            count += len(chunk)
            if time.time() - time1 > 2:
                p = count / length * 100
                speed = (count - count_tmp) / 1024  / 2
                count_tmp = count
                print(name + ': ' + formatFloat(p) + '%' + ' Speed: ' + formatFloat(speed) + 'Kb/S')
                time1 = time.time()
    f.close()


def formatFloat(num):
    return '{:.2f}'.format(num)


def createConfigFile():
    with open('bubble.json', 'w') as f:
        json.dump({'software_version': ver, 'server_address': 'microfish.club', 'server_port': '8760'}, f)


def readConfigFile():
    with open('bubble.json') as f:
        return json.load(f)


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
    while True:
        while True:
            try:
                userID = int(input('User ID: '))
                pwd = input('Password: ')
                break
            except ValueError:
                print('userID 只能为数字。')
        msg = socket.userRegister(userID, pwd)
        if msg:
            print('注册成功。')
            return
        else:
            print('账号已存在。')


def mainFunc(socket: user.userHandle):
    userID = int(input('User ID: '))
    pwd = input('Password: ')
    socket.login(userID, pwd)
    print('Login Successfully')
    while True:
        try:
            showMainMenu()
            choice = input('>')
            if choice == '1':
                chatSystem(socket)
            elif choice == '2':
                friendSystem(socket)
            elif choice == '3':
                friendSystem(socket)
        except KeyboardInterrupt:
            break


def chatSystem(socket: user.userHandle):
    print(socket.getFriendList())
    friendID = int(input('Input Friend ID :'))
    threading.Timer(3, socket.recallMsg, args=(friendID, 3)).start()
    print('chat with {}'.format(friendID))
    while True:
        showMenu((['1', '发送文字'], ['2', '发送图片'], ['3', '发送文件'], ['4', '发送语音']))
        choice = input('>')
        if choice == '1':
            while True:
                try:
                    msg = input()
                    socket.sendMsg(friendID, msg)
                except KeyboardInterrupt:
                    break
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
            print('好友请求已经发送。')
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
