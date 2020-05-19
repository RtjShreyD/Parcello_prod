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
# kcw = KeyClipWriter(bufSize=32)

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


@Socketrunthread.conn.subscribe
def onMessage(m):
    print(m)
    if m == "open":
        ard_snd("*")


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
            cams = False
            print("Transaction Complete, Ready for another transaction") #Here we can notify the user about a complete transaction


try:
    t = Socketrunthread(cam, False)
    t.start()

except KeyboardInterrupt:
    pass