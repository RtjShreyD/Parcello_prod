import asyncio
import json
import time
import serial
from rtcbot import Websocket, RTCConnection, CVCamera

cam = CVCamera()
conn = RTCConnection()
conn.video.putSubscription(cam)

try:
    arduino = serial.Serial('/dev/ttyUSB0', 9600, timeout=.1)
    time.sleep(1)
except:
    print("Arduino not connected")


async def connect():
    ws = Websocket("http://localhost:8080/xyz")
    remoteDescription = await ws.get()
    print("The remote description is of type: " + str(type(remoteDescription)) + "\n" )

    robotDescription = await conn.getLocalDescription(remoteDescription)
    
    print("The robot description is of type: " + str(type(robotDescription)) + "\n" )
    ws.put_nowait(robotDescription)
    print("Started WebRTC")
    await ws.close()


def ard_snd(msg):
    try:
        arduino.write(msg.encode())
    except:
        print("Arduino not connected")


@conn.subscribe
def onMessage(m):
    print(m)
    if m == "open":
        ard_snd("*")
  

asyncio.ensure_future(connect())
try:
    asyncio.get_event_loop().run_forever()

except KeyboardInterrupt:
    pass

finally:
    cam.close()
    conn.close()