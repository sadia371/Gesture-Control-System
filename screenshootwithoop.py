import cv2
import numpy as np
import HandTrackingModule as htm
import math
import pyautogui
import time

class ScreenshotCapturer:
    def __init__(self):
        self.capture_flag = False

    def check_capture(self, lmList):
        if len(lmList) >= 21:  # Ensure lmList contains at least 21 elements
            if lmList[8][2] < lmList[6][2] and lmList[12][2] < lmList[10][2]:
                if lmList[16][2] > lmList[18][2] and lmList[20][2] > lmList[18][2]:
                    self.capture_flag = True
                    print("Capture flag set")
                else:
                    print("Condition for index 16 and 20 not met")
            else:
                print("Condition for index 8 and 12 not met")
        else:
            print("lmList does not contain enough elements")
            self.capture_flag = False

# Initialize hand tracking module
detector = htm.HandDetector(detectionCon=0.7)
screenshot_capturer = ScreenshotCapturer()

# Camera setup
cap = cv2.VideoCapture(0)
cap.set(3, 640)
cap.set(4, 480)

while True:
    success, img = cap.read()
    if not success:
        print("Error: Failed to capture image.")
        break

    # Hand tracking
    img = detector.findHands(img)
    lmList = detector.findPosition(img, draw=False)

    if lmList:
        # Check if screenshot should be captured
        screenshot_capturer.check_capture(lmList)

        # Capture screenshot if the capture_flag is True
        if screenshot_capturer.capture_flag:
            screenshot = pyautogui.screenshot()
            screenshot_path = f"screenshot_{int(time.time())}.png"
            screenshot.save(screenshot_path)
            print(f"Screenshot saved at: {screenshot_path}")
            screenshot_capturer.capture_flag = False  # Reset capture flag

        # Visual feedback on the hand positions
        for lm in lmList:
            x, y = lm[1], lm[2]
            cv2.circle(img, (x, y), 8, (255, 0, 255), cv2.FILLED)

    # Display video feed
    cv2.imshow("Img", img)

    # Exit loop if 'q' is pressed
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release resources
cap.release()
cv2.destroyAllWindows()
