import IMClient as im
from IMClient.user import loginError

if __name__ == '__main__':
    while True:
        try:
            im.service.welcome()
            a = im.userHandle()
            id = input('User ID: ')
            pwd = input('Password: ')
            a.login(872702913, '(imp@h01)')
            a.userList()
            im.service.showMenu()
            choice=input('>')
        except loginError:
            print('登录失败，请检查账号和密码')
