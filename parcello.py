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

kcw = KeyClipWriter(bufSize=32)

conf = Conf("config/config.json")
up = Uploader(conf)

path = ''

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
    global PS, trans, cams
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
            print("Trans set to :" + str(trans))
            cams = False
            print("Cams set to :" + str(cams))
            print("Transaction Complete, Ready for another transaction") #Here we can notify the user about a complete transaction


@cam.subscribe
def onFrame(frame):
    
    global path, trans
        
    fr = frame
    fr = imutils.resize(fr, width=600)
    display.put_nowait(frame)

    if cams and trans==0:
        
        if not kcw.recording:
            timestamp = datetime.datetime.now()
            path = "{}/{}.avi".format("vids/", timestamp.strftime("%Y%m%d-%H%M%S"))
            kcw.start(path, cv2.VideoWriter_fourcc(*"MJPG"), 30)
            print("Inside the if main for rec, cams, trans are " + str(cams) + " ," + str(trans))
        
    kcw.update(fr)  

    if kcw.recording and trans == 1: ## For when user opens from webrtc page and box get closed by auto
        print("Rec Stop with transaction Complete" + " " + path)
        kcw.finish()
        # up.send(path)
        trans = 0

    if kcw.recording:
        print("Rec")


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
                if m == "open":
                    ard_snd("*")
                if m == "end":
                    self.finish()


    def start_loop(self):
        try:        
            asyncio.set_event_loop(self.loop)
            self.loop.run_forever()        
        except KeyboardInterrupt:
            pass           


    def finish(self):
        try:
            self.conn.close()
            self.loop.stop()
            self.stop_event = False
            self.thread.join()
            print("Thread stopped")
        except RuntimeError:
            print("Exception Handled successfully")


    async def connect(self):
        global cams
        ws = Websocket("http://localhost:8080/xyz")
        remoteDescription = await ws.get()
        print("The remote description is of type: " + str(type(remoteDescription)) + "\n" )

        robotDescription = await self.conn.getLocalDescription(remoteDescription)
        
        print("The robot description is of type: " + str(type(robotDescription)) + "\n" )
        ws.put_nowait(robotDescription)
        print("Started WebRTC")
        cams = True
        print("Cams set to :" + str(cams))
        await ws.close()



try:

    t2 = Thread(target=resp)
    t2.daemon = True
    t2.start()

    while True:
        t = Socketrunthread(cam, False)
        t.start()
        time.sleep(30)
        t.finish()
        time.sleep(10)

except KeyboardInterrupt:
    pass