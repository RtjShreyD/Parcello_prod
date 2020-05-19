import asyncio
import json
import time
from rtcbot import Websocket, RTCConnection
from threading import Thread


class Socketrunthread():

    def __init__(self, stop_event, addr):
        self.thread = None
        self.conn = RTCConnection()
        self.stop_event = stop_event
        self.addr = addr
        asyncio.ensure_future(self.connect())
        self.loop = asyncio.get_event_loop()

    def start(self):
        if not self.stop_event:
            self.thread = Thread(target=self.start_loop, args=())
            self.thread.start()
            # time.sleep(3)
            # self.finish()


    def start_loop(self):
        
        try:        
            asyncio.set_event_loop(self.loop)
            self.loop.run_forever()

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

        ws = Websocket(self.addr)
        remoteDescription = await ws.get()
        print("The remote description is of type: " + str(type(remoteDescription)) + "\n" )

        robotDescription = await self.conn.getLocalDescription(remoteDescription)
        
        print("The robot description is of type: " + str(type(robotDescription)) + "\n" )
        ws.put_nowait(robotDescription)
        print("Started WebRTC")
        await ws.close()

try:
    base_addr = "http://localhost:8080/"
    for x in range(1,10):
        new_addr = base_addr + str(x)
        t = Socketrunthread(False, new_addr)
        t.start()

except KeyboardInterrupt:
    pass