import cv2
import json
import time
import serial
import imutils
import asyncio
import datetime
import threading
from utils.conf import Conf
from imutils.io import TempFile
from imutils.video import VideoStream
from Logix_dir.MotionWriter import KeyClipWriter, Uploader
from rtcbot import Websocket, RTCConnection, CVCamera, CVDisplay

cam = CVCamera()
conn = RTCConnection()
conn.video.putSubscription(cam)

display = CVDisplay()
kcw = KeyClipWriter(bufSize=32)

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


async def connect():
    global cams

    ws = Websocket("http://localhost:8080/xyz")
    remoteDescription = await ws.get()
    print("The remote description is of type: " + str(type(remoteDescription)) + "\n" )

    robotDescription = await conn.getLocalDescription(remoteDescription)
    
    print("The robot description is of type: " + str(type(robotDescription)) + "\n" )
    ws.put_nowait(robotDescription)
    print("Started WebRTC")
    cams = True
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


@cam.subscribe
def onFrame(frame):
    
    global path
    # bwframe = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    # display.put_nowait(bwframe)
    
    fr = frame
    fr = imutils.resize(fr, width=600)

    if cams and trans==0:
        
        if not kcw.recording:
            timestamp = datetime.datetime.now()
            path = "{}/{}.avi".format("vids/", timestamp.strftime("%Y%m%d-%H%M%S"))
            kcw.start(path, cv2.VideoWriter_fourcc(*"MJPG"), 30)
        
    kcw.update(fr)  

    if kcw.recording and trans == 1: ## For when user opens from webrtc page and box get closed by auto
        print("Rec Stop with transaction Complete" + " " + path)
        kcw.finish()
        up.send(path)

    if kcw.recording:
        print("Rec")




t1 = threading.Thread(target=start_loop, args=(loop,))
t1.start()

print("Threaded")

t2 = threading.Thread(target=resp)
t2.daemon = True
t2.start()
