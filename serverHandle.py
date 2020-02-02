import threading
import IMServer

a = IMServer.IMServerSocket('127.0.0.1', 18760)
mainloop = threading.Thread(target=a.mainLoop)
cleanUp = threading.Timer(60, a.userListCleanup)
try:
    mainloop.start()
    cleanUp.start()
except:
    pass
