import cv2
import time
import numpy as np
import math
from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
import HandTrackingModule as htm  # Ensure HandTrackingModule is correctly implemented and imported

class VolumeController:
    def __init__(self):
        # Initialize the audio endpoint volume interface
        devices = AudioUtilities.GetSpeakers()
        interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
        self.volume = cast(interface, POINTER(IAudioEndpointVolume))
        self.volRange = self.volume.GetVolumeRange()
        self.minVol = self.volRange[0]
        self.maxVol = self.volRange[1]

    def set_volume(self, vol):
        # Set the system volume to the specified level
        self.volume.SetMasterVolumeLevel(vol, None)

    def get_volume_range(self):
        # Return the minimum and maximum volume levels
        return self.minVol, self.maxVol

class BaseApp:
    def __init__(self, wCam=640, hCam=480):
        # Initialize the webcam and set the dimensions
        self.cap = cv2.VideoCapture(0)  # Use 0 for the default webcam
        self.cap.set(3, wCam)
        self.cap.set(4, hCam)
        self.pTime = 0

    def read_frame(self):
        # Capture a frame from the webcam
        success, img = self.cap.read()
        if not success:
            print("Error: Failed to capture image.")
            return None
        return img

    def display_frame(self, img):
        # Display the frame with FPS overlay
        cTime = time.time()
        fps = 1 / (cTime - self.pTime)
        self.pTime = cTime
        cv2.putText(img, f'FPS: {int(fps)}', (40, 50), cv2.FONT_HERSHEY_COMPLEX, 1, (255, 0, 0), 3)
        cv2.imshow("Img", img)

    def release(self):
        # Release the webcam and close all OpenCV windows
        self.cap.release()
        cv2.destroyAllWindows()

class HandVolumeApp(BaseApp):
    def __init__(self, wCam=640, hCam=480, detectionCon=0.7):
        super().__init__(wCam, hCam)
        # Initialize the hand detector and volume controller
        self.detector = htm.HandDetector(detectionCon=detectionCon)
        self.volumeController = VolumeController()
        self.minVol, self.maxVol = self.volumeController.get_volume_range()
        self.vol = 0
        self.volBar = 400
        self.volPer = 0

    def fingers_up(self, lmList):
        # Determine which fingers are up
        fingers = []
        # Thumb
        if lmList[4][1] > lmList[3][1]:
            fingers.append(1)
        else:
            fingers.append(0)
        # 4 Fingers
        for id in range(8, 21, 4):
            if lmList[id][2] < lmList[id - 2][2]:
                fingers.append(1)
            else:
                fingers.append(0)
        return fingers

    def run(self):
        while True:
            # Capture a frame from the webcam
            img = self.read_frame()
            if img is None:
                break

            # Detect hands and landmarks in the frame
            img = self.detector.findHands(img)
            lmList = self.detector.findPosition(img, draw=False)
            if len(lmList) != 0:
                # Check if the gesture with only index finger and thumb up is detected
                fingers = self.fingers_up(lmList)
                if fingers[1] == 1 and fingers[0] == 1 and fingers[2] == 0 and fingers[3] == 0 and fingers[4] == 0:
                    # Get coordinates of the thumb tip and index finger tip
                    x1, y1 = lmList[4][1], lmList[4][2]
                    x2, y2 = lmList[8][1], lmList[8][2]
                    cx, cy = (x1 + x2) // 2, (y1 + y2) // 2

                    # Draw circles and lines to visualize the gesture
                    cv2.circle(img, (x1, y1), 15, (255, 0, 255), cv2.FILLED)
                    cv2.circle(img, (x2, y2), 15, (255, 0, 255), cv2.FILLED)
                    cv2.line(img, (x1, y1), (x2, y2), (255, 0, 255), 3)
                    cv2.circle(img, (cx, cy), 15, (255, 0, 255), cv2.FILLED)

                    # Calculate the distance between the thumb and index finger
                    length = math.hypot(x2 - x1, y2 - y1)

                    # Map the distance to the volume range and update volume
                    self.vol = np.interp(length, [50, 300], [self.minVol, self.maxVol])
                    self.volBar = np.interp(length, [50, 300], [400, 150])
                    self.volPer = np.interp(length, [50, 300], [0, 100])
                    self.volumeController.set_volume(self.vol)

                    # Change color of the center circle if the fingers are very close
                    if length < 50:
                        cv2.circle(img, (cx, cy), 15, (0, 255, 0), cv2.FILLED)

            # Draw the volume bar and percentage
            cv2.rectangle(img, (50, 150), (85, 400), (255, 0, 255), 3)
            cv2.rectangle(img, (50, int(self.volBar)), (85, 400), (255, 0, 255), cv2.FILLED)
            cv2.putText(img, f'{int(self.volPer)} %', (40, 450), cv2.FONT_HERSHEY_COMPLEX, 1, (255, 0, 255), 3)

            # Display the frame
            self.display_frame(img)

            # Exit on 'q' key press
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        # Release resources
        self.release()

if __name__ == "__main__":
    # Run the application
    app = HandVolumeApp()
    app.run()
