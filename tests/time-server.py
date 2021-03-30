
import sys 
import time
import sysv_ipc

key = 666

try:
    mq = sysv_ipc.MessageQueue(key, sysv_ipc.IPC_CREX)
except ExistentialError:
    print("Message queue", key, "already exsits, terminating.")
    sys.exit(1)

print("Starting time server.")

while True:
    m, t = mq.receive()
    if t == 1:
        dt = time.asctime()      
        message = str(dt).encode()
        mq.send(message, type=3)
    if t == 2:
        print("Terminating time server.")
        mq.remove()
        break

