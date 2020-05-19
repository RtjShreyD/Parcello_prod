import asyncio
import json
import time
from rtcbot import Websocket, RTCConnection, CVCamera
from threading import Thread, Event

cam = CVCamera()

class Socketrunthread():

    def __init__(self, cam, stop_event):
        self.thread = None
        self.conn = RTCConnection()
        self.cam = cam
        self.stop_event = stop_event
        self.conn.video.putSubscription(cam)

        asyncio.ensure_future(self.connect())
        self.loop = asyncio.get_event_loop()

    def start(self):
        if not self.stop_event:
            self.thread = Thread(target=self.start_loop, args=())
            self.thread.start()

    def start_loop(self):
        
        try:        
            asyncio.set_event_loop(self.loop)
            # print("Next stmt loop forever")
            self.loop.run_forever()
            # print("After run forever")

        except KeyboardInterrupt:
            pass           

    def finish(self):
        # self.cam.close()
        self.conn.close()
        self.loop.stop()
        self.stop_event = False
        self.thread.join()
        print("Thread stopped")

    async def connect(self):

        ws = Websocket("http://localhost:8080/xyz")
        remoteDescription = await ws.get()
        print("The remote description is of type: " + str(type(remoteDescription)) + "\n" )

        robotDescription = await self.conn.getLocalDescription(remoteDescription)
        
        print("The robot description is of type: " + str(type(robotDescription)) + "\n" )
        ws.put_nowait(robotDescription)
        print("Started WebRTC")
        await ws.close()

try:
    t = Socketrunthread(cam, False)
    t.start()
    print("Started 1 should work 20 sec")
    time.sleep(20)
    t.finish()
    print("Finish 1 sleep 15")
    time.sleep(15)
    t = Socketrunthread(cam, False)
    t.start()
    print("Started 2 should work 20 sec")
    time.sleep(20)
    t.finish()
    print("Finish 2 sleep 5")
    time.sleep(5)

except KeyboardInterrupt:
    pass