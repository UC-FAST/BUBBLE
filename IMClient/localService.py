import requests
import prettytable as pt


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
    print('main menu')
    tb.add_row([1, 'login'])
    tb.add_row([2, 'register'])
    tb.add_row([3, 'exit'])
    print(tb)

def showMainMenu():
    pass

def showSetUpMenu():
    pass

