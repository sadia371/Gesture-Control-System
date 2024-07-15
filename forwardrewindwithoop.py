import cv2
import math
import pyautogui
import HandTrackingModule as htm

class VideoController:
    def __init__(self, detector):
        self.detector = detector

    def control_video(self):
        cap = cv2.VideoCapture(0)
        cap.set(3, 640)
        cap.set(4, 480)

        while True:
            success, img = cap.read()
            if not success:
                print("Error: Failed to capture image.")
                break

            # Hand tracking
            img = self.detector.findHands(img)
            lmList = self.detector.findPosition(img, draw=False)

            if lmList:
                # Video forwarding control (use thumb and pinky distance)
                x1, y1 = lmList[4][1], lmList[4][2]
                x5, y5 = lmList[20][1], lmList[20][2]
                forward_length = math.hypot(x5 - x1, y5 - y1)

                # Video rewinding control (use thumb and ring finger distance)
                x4, y4 = lmList[16][1], lmList[16][2]
                rewind_length = math.hypot(x4 - x1, y4 - y1)

                if forward_length < 50:
                    pyautogui.press('right')
                    print("Forwarding video")

                if rewind_length < 50:
                    pyautogui.press('left')
                    print("Rewinding video")

                # Visual feedback on the hand positions
                cv2.circle(img, (lmList[20][1], lmList[20][2]), 15, (255, 0, 255), cv2.FILLED)
                cv2.circle(img, (lmList[16][1], lmList[16][2]), 15, (255, 0, 255), cv2.FILLED)

            # Display video feed
            cv2.imshow("Img", img)

            # Exit loop if 'q' is pressed
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        # Release resources
        cap.release()
        cv2.destroyAllWindows()

def main():
    # Initialize hand tracking module
    detector = htm.HandDetector(detectionCon=0.7)

    # Initialize video controller
    video_controller = VideoController(detector)

    # Control the video
    video_controller.control_video()

if __name__ == "__main__":
    main()
