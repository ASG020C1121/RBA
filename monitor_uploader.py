import threading
import time

def process():
    print('Process Start')
    time.sleep(3)
    print('Process End')


print('Main Start')

threadA = threading.Thread(target=process)
threadA.setDaemon(True)
threadA.start()

time.sleep(1)

print('Main End')