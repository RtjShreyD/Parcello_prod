import asyncio
import json
import time
import serial
import threading
from rtcbot import Websocket, RTCConnection, CVCamera

cam = CVCamera()
conn = RTCConnection()
conn.video.putSubscription(cam)

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
    while True:
        data = arduino.readline()
        print("Response from Arduino is: " + str(data))


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