### Installation and Running Instructions

#### On Local system or Cloud server:

1. Install and make a venv:  <br /> 
Install -  <br />
    `sudo apt-get install python3-venv` <br />
Make -  <br />
    `python3 -m venv rtc_env` <br />
    `source rtc_env/bin/activate` <br />
    `pip install -U pip` <br />

2. Install AIORTC, AIOHTTP and opencv: <br />
    `pip install aiohttp aiortc opencv-contrib-python` <br />

3. Install dependencies: <br /> 
    `sudo apt-get install build-essential python3-numpy python3-cffi python3-aiohttp \
    libavformat-dev libavcodec-dev libavdevice-dev libavutil-dev \
    libswscale-dev libswresample-dev libavfilter-dev libopus-dev \
    libvpx-dev pkg-config libsrtp2-dev python3-opencv pulseaudio`

4. Install rtcbot library: <br />
    `pip install rtcbot`

5. Clone the repository and cd into the dir.

6. Run `python m_kb_svr.py` in one terminal. OR run it on a server Instance as applicable.

7. Run `python remote_box.py` in other terminal after making sure the Websocket is correctly defined in the file as per use case.

8. Open http://Your_Server_Public_IPv4_Address:8080/{remote-name} if running on server OR http://localhost:8080/{remote-name} if running on local network.

