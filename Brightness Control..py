import cv2
import numpy as np
import HandTrackingModule as htm
import math
import wmi


class ScreenBrightnessController:
    def __init__(self, wCam=640, hCam=480, detectionCon=0.7):
     # Initialize camera properties and hand detection confidence
        self.wCam = wCam
        self.hCam = hCam
        self.detectionCon = detectionCon

        # Define brightness range (0-100)
        self.brightness_min = 0
        self.brightness_max = 100

        # Initialize camera capture, set properties, and hand detector
        self.cap = cv2.VideoCapture(0)
        self.cap.set(3, self.wCam)
        self.cap.set(4, self.hCam)
        self.detector = htm.HandDetector(detectionCon=self.detectionCon)

        # Create a connection to the WMI service for screen brightness control
        self.c = wmi.WMI(namespace='wmi')

    def calculate_distance(self, lmList, point1, point2):
        # Calculate the Euclidean distance between two specified landmarks
        x1, y1 = lmList[point1][1:]
        x2, y2 = lmList[point2][1:]
        distance = math.hypot(x2 - x1, y2 - y1)
        return distance, (x1, y1), (x2, y2)

    def set_brightness(self, brightness):
        # Set the screen brightness using WMI
        self.c.WmiMonitorBrightnessMethods()[0].WmiSetBrightness(brightness, 0)

    def fingers_down(self, lmList):
        # Check if both the ring finger and pinky finger are down
        return lmList[16][2] > lmList[14][2] and lmList[20][2] > lmList[18][2]

    def run(self):
        while True:
            # Capture video frame
            success, img = self.cap.read()
            if not success:
                print("Error: Failed to capture image.")
                break

            # Detect hands in the frame
            img = self.detector.findHands(img)
            lmList = self.detector.findPosition(img, draw=False)

            # If hands are detected
            if lmList:
                # Check if both fingers are down
                if self.fingers_down(lmList):
                    # Calculate distance between thumb and middle finger
                    distance, thumb_pos, middle_pos = self.calculate_distance(lmList, 4, 12)

                    # Map the distance to brightness range
                    brightness = np.interp(distance, [20, 250], [self.brightness_min, self.brightness_max])
                    brightness = int(brightness)

                    # Set the screen brightness
                    self.set_brightness(brightness)

                    # Visual feedback: draw circles at thumb and middle finger positions
                    cv2.circle(img, thumb_pos, 15, (255, 0, 255), cv2.FILLED)
                    cv2.circle(img, middle_pos, 15, (255, 0, 255), cv2.FILLED)

            # Display processed frame
            cv2.imshow("Img", img)

            # Exit loop if 'q' is pressed
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        # Release resources
        self.cap.release()
        cv2.destroyAllWindows()


if __name__ == "__main__":
    # Create instance of ScreenBrightnessController and run the program
    controller = ScreenBrightnessController()
    controller.run()
