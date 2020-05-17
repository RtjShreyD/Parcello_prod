import asyncio
import json
import time
from rtcbot import Websocket, RTCConnection, CVCamera
from threading import Thread

cam = CVCamera()
conn = RTCConnection()
conn.video.putSubscription(cam)

class Socketrunthread():

    def __init__(self, loop, conn, cam):
        self.thread = None
        self.loop = loop
        self.conn = conn
        self.cam = cam

    def start(self):
        self.thread = Thread(target=self.start_loop, args=())
        self.thread.start()

    def start_loop(self):
        
        try:        
            asyncio.set_event_loop(self.loop)
            print("Next stmt loop forever")
            loop.run_forever()

        except KeyboardInterrupt:
            pass           

    def finish(self):
        self.cam.close()
        self.conn.close()


async def connect():

    ws = Websocket("http://localhost:8080/xyz")
    remoteDescription = await ws.get()
    print("The remote description is of type: " + str(type(remoteDescription)) + "\n" )

    robotDescription = await conn.getLocalDescription(remoteDescription)
    
    print("The robot description is of type: " + str(type(robotDescription)) + "\n" )
    ws.put_nowait(robotDescription)
    print("Started WebRTC")
    await ws.close()

asyncio.ensure_future(connect())
loop = asyncio.get_event_loop()

t = Socketrunthread(loop, conn, cam)
t.start()
print("Going to sleep 40")
time.sleep(10)
t.finish()
print("Going to sleep 10 after finish")
time.sleep(5)
print("Starting again try refreshing")
t.start()