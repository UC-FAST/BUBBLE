import requests
from pprint import pprint


class service():
    @staticmethod
    def version():
        return 'v0.0.1'

    @classmethod
    def updateChecker(cls):
        url = 'https://microfish.club/bubble/update.json'
        r = requests.get(url).json()
        if not cls.version() == r['version']:
            print('检测到新版本，正在下载更新')
            r = requests.get('https://microfish.club/bubble/bubble.zip')

    @classmethod
    def welcome(cls):
        print('欢迎使用Bubble {}'.format(cls.version()))
        cls.updateChecker()

    @staticmethod
    def showMenu():
        print('menu')
        menu = {1: 'chat', 2: 'friend list', 3: 'setup'}
        for key, value in zip(menu.keys(), menu.values()):
            print(key, value)
