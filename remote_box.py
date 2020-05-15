import asyncio
import json
import time
from rtcbot import Websocket, RTCConnection, CVCamera

keystates = {"w": False, "a": False, "s": False, "d": False}

cam = CVCamera()
conn = RTCConnection()
conn.video.putSubscription(cam)

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
    # global keystates
    # if m["keyCode"] == 87:  # W
    #     keystates["w"] = m["type"] == "keydown"
    # elif m["keyCode"] == 83:  # S
    #     keystates["s"] = m["type"] == "keydown"
    # elif m["keyCode"] == 65:  # A
    #     keystates["a"] = m["type"] == "keydown"
    # elif m["keyCode"] == 68:  # D
    #     keystates["d"] = m["type"] == "keydown"
    # print({
    #         "forward": keystates["w"] * 1 - keystates["s"] * 1,
    #         "leftright": keystates["d"] * 1 - keystates["a"] * 1,
    #     })



asyncio.ensure_future(connect())
try:
    asyncio.get_event_loop().run_forever()

except KeyboardInterrupt:
    pass

finally:
    cam.close()
    conn.close()