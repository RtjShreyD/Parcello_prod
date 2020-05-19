import cv2
import json
import time
import serial
import imutils
import asyncio
import datetime
from utils.conf import Conf
from threading import Thread
from imutils.io import TempFile
from imutils.video import VideoStream
from Logix_dir.MotionWriter import KeyClipWriter, Uploader
from rtcbot import Websocket, RTCConnection, CVCamera, CVDisplay

cam = CVCamera()
display = CVDisplay()

trans = 0
PS = False # pin state resp from Arduino
cams = False # flag var for webrtc video started

conf = Conf("config/config.json")
up = Uploader(conf)

path = ''

try:
    arduino = serial.Serial('/dev/ttyUSB0', 9600, timeout=.1)
    time.sleep(1)
except:
    print("Arduino not connected")


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
            print("Ok")

            @self.conn.subscribe
            def OnMessage(m):
                print(m)



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
    time.sleep(20)
    t.finish()
    time.sleep(10)
    t = Socketrunthread(cam, False)
    t.start()


except KeyboardInterrupt:
    pass