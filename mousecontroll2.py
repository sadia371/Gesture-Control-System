import cv2
import numpy as np
import HandTrackingModule as htm
import math
import pyautogui

class MouseControl:
    def __init__(self, wCam=640, hCam=480, detectionCon=0.7, screenRatio=5, clickThreshold=40, smoothing=5):
        self.wCam = wCam
        self.hCam = hCam
        self.detector = htm.HandDetector(detectionCon=detectionCon)
        self.screenWidth, self.screenHeight = pyautogui.size()
        self.screenRatio = screenRatio
        self.clickThreshold = clickThreshold
        self.smoothing = smoothing
        self.cap = cv2.VideoCapture(0)
        self.cap.set(3, self.wCam)
        self.cap.set(4, self.hCam)
        self.prev_x, self.prev_y = 0, 0
        self.curr_x, self.curr_y = 0, 0

    def move_cursor(self, lmList):
        if lmList:
            # Map hand coordinates to screen coordinates
            x, y = lmList[8][1:]
            x = np.interp(x, [0, self.wCam], [0, self.screenWidth])
            y = np.interp(y, [0, self.hCam], [0, self.screenHeight])

            # Smooth the cursor movement
            self.curr_x = self.prev_x + (x - self.prev_x) / self.smoothing
            self.curr_y = self.prev_y + (y - self.prev_y) / self.smoothing

            # Move the cursor
            pyautogui.moveTo(self.curr_x, self.curr_y)

            # Update previous positions
            self.prev_x, self.prev_y = self.curr_x, self.curr_y

    def click_mouse(self, lmList):
        if len(lmList) >= 21:  # Ensure lmList contains at least 21 landmarks
            thumbTipX, thumbTipY = lmList[4][1:]
            indexTipX, indexTipY = lmList[8][1:]
            middleTipX, middleTipY = lmList[12][1:]
            ringTipX, ringTipY = lmList[16][1:]
            pinkyTipX, pinkyTipY = lmList[20][1:]

            # Calculate distances between thumb and index, thumb and middle, ring and pinky
            index_length = math.hypot(indexTipX - thumbTipX, indexTipY - thumbTipY)
            middle_length = math.hypot(middleTipX - thumbTipX, middleTipY - thumbTipY)
            ring_pinky_length = math.hypot(ringTipX - pinkyTipX, ringTipY - pinkyTipY)

            # Check if pinky and ring fingers are close
            if ring_pinky_length < self.clickThreshold:
                # Left click with index and thumb
                if index_length < self.clickThreshold and middle_length > self.clickThreshold:
                    pyautogui.click(button='left')
                # Right click with middle and thumb
                elif middle_length < self.clickThreshold and index_length > self.clickThreshold:
                    pyautogui.click(button='right')

    def run(self):
        while True:
            success, img = self.cap.read()
            if not success:
                print("Error: Failed to capture image.")
                break

            img = self.detector.findHands(img)
            lmList = self.detector.findPosition(img, draw=False)

            self.move_cursor(lmList)
            self.click_mouse(lmList)

            cv2.imshow("Img", img)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        self.cap.release()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    mouse_control = MouseControl()
    mouse_control.run()
