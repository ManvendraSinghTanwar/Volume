import cv2
import numpy as np
import websockets
import asyncio
import json
import base64
import time
import math
from HandTrackingModule import HandDetector
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL

# Set up volume control
devices = AudioUtilities.GetSpeakers()
interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
volume = cast(interface, POINTER(IAudioEndpointVolume))

# Get the volume range
volRange = volume.GetVolumeRange()
minVol, maxVol = volRange[0], volRange[1]

# Initialize webcam and hand detector
cap = cv2.VideoCapture(0)
detector = HandDetector(detectionCon=0.7, maxHands=1)

# WebSocket server to stream video and volume data
async def video_stream(websocket, path):
    while cap.isOpened():
        success, img = cap.read()
        if not success:
            continue

        # Find hand and get landmark positions
        img = detector.findHands(img)
        lmList = detector.findPosition(img, draw=False)

        vol = 0
        if len(lmList) != 0:
            x1, y1 = lmList[4][1], lmList[4][2]  # Thumb
            x2, y2 = lmList[8][1], lmList[8][2]  # Index Finger
            length = math.hypot(x2 - x1, y2 - y1)

            # Interpolate the length into volume level
            vol = np.interp(length, [50, 300], [minVol, maxVol])
            volume.SetMasterVolumeLevel(vol, None)

        # Convert the image to base64 for sending over WebSocket
        _, buffer = cv2.imencode('.jpg', img)
        frame = base64.b64encode(buffer).decode('utf-8')

        # Create data to send (volume and frame)
        data = {
            "volume": np.interp(vol, [minVol, maxVol], [0, 100]),  # Percentage volume
            "frame": f"data:image/jpeg;base64,{frame}"  # Base64 encoded image
        }

        # Send data to the frontend
        await websocket.send(json.dumps(data))

        await asyncio.sleep(0.01)

# Start the WebSocket server
start_server = websockets.serve(video_stream, "localhost", 8765)

# Run the WebSocket server
asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()

cap.release()
