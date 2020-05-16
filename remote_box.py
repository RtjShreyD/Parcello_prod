import asyncio
import json
import time
import serial
import threading
from rtcbot import Websocket, RTCConnection, CVCamera

cam = CVCamera()
conn = RTCConnection()
conn.video.putSubscription(cam)

trans = 0
PS = False

try:
    arduino = serial.Serial('/dev/ttyUSB0', 9600, timeout=.1)
    time.sleep(1)
except:
    print("Arduino not connected")


def ard_snd(msg):
    try:
        arduino.write(msg.encode())
    except:
        print("Arduino not connected")


def resp():
    global PS, trans
    prev_st = 0
    curr_st = 0

    while True:
        data = arduino.readline()
        if data:
            temp = data.decode()
            PS = temp.rstrip()
            print("PS changed to  " + PS)

            if PS == "True":
                prev_st = 1
                curr_st = 1

            if PS == "False" and prev_st == 1:
                curr_st = 0
           
        if prev_st != curr_st:
            prev_st = 0
            trans = 1
            print("Transaction Complete, Ready for another transaction") #Here we can notify the user about a complete transaction


async def connect():
    ws = Websocket("http://localhost:8080/xyz")
    remoteDescription = await ws.get()
    print("The remote description is of type: " + str(type(remoteDescription)) + "\n" )

    robotDescription = await conn.getLocalDescription(remoteDescription)
    
    print("The robot description is of type: " + str(type(robotDescription)) + "\n" )
    ws.put_nowait(robotDescription)
    print("Started WebRTC")
    await ws.close()


@conn.subscribe
def onMessage(m):
    print(m)
    if m == "open":
        ard_snd("*")
  


asyncio.ensure_future(connect())
loop = asyncio.get_event_loop()

def start_loop(loop):
    try:        
        asyncio.set_event_loop(loop)
        print("Next stmt loop forever")
        loop.run_forever()

    except KeyboardInterrupt:
        pass

    finally:
        cam.close()
        conn.close()


t1 = threading.Thread(target=start_loop, args=(loop,))
t1.start()

print("Threaded")

t2 = threading.Thread(target=resp)
t2.daemon = True
t2.start()