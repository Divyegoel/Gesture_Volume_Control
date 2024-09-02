import cv2
import time
import numpy as np
import HandTrackingModule as htm
import subprocess

# Video capture resolution
wCam, hCam = 640, 480

cap = cv2.VideoCapture(0)  # Use 0 if 1 doesn't work
cap.set(3, wCam)
cap.set(4, hCam)
cap.set(cv2.CAP_PROP_FPS, 30)  # Set FPS for faster capture
pTime = 0

detector = htm.handDetector(detectionCon=0.7, maxHands=1)

def set_volume(volume):
    """Sets the system volume using AppleScript."""
    volume = max(0, min(volume, 100))
    script = f"set volume output volume {volume}"
    subprocess.run(["osascript", "-e", script], check=False)

volBar = 400
volPer = 0
area = 0
colorVol = (255, 0, 0)

while True:
    success, img = cap.read()
    if not success:
        print("Failed to grab frame")
        break

    # Start timing
    start_time = time.time()

    # Find Hand
    img = detector.findHands(img)
    lmList, bbox = detector.findPosition(img, draw=True)
    if len(lmList) != 0:

        # Filter based on size
        area = (bbox[2] - bbox[0]) * (bbox[3] - bbox[1]) // 100
        if 250 < area < 1000:

            # Find Distance between index and Thumb
            length, img, lineInfo = detector.findDistance(4, 8, img)

            # Convert Volume
            volBar = np.interp(length, [50, 200], [400, 150])
            volPer = np.interp(length, [50, 200], [0, 100])

            # Reduce Resolution to make it smoother
            smoothness = 10
            volPer = smoothness * round(volPer / smoothness)

            # Set system volume
            set_volume(volPer)

            # Check fingers up
            fingers = detector.fingersUp()

            # If pinky is down set volume
            if not fingers[4]:
                cv2.circle(img, (lineInfo[4], lineInfo[5]), 15, (0, 255, 0), cv2.FILLED)
                colorVol = (0, 255, 0)
            else:
                colorVol = (255, 0, 0)

    # Drawings
    cv2.rectangle(img, (50, 150), (85, 400), (255, 0, 0), 3)
    cv2.rectangle(img, (50, int(volBar)), (85, 400), (255, 0, 0), cv2.FILLED)
    cv2.putText(img, f'{int(volPer)} %', (40, 450), cv2.FONT_HERSHEY_COMPLEX,
                1, (255, 0, 0), 3)

    # Frame rate
    cTime = time.time()
    fps = 1 / (cTime - pTime)
    pTime = cTime
    cv2.putText(img, f'FPS: {int(fps)}', (40, 50), cv2.FONT_HERSHEY_COMPLEX,
                1, (255, 0, 0), 3)

    # End timing and calculate processing time
    process_time = (time.time() - start_time) * 1000  # in milliseconds
    if process_time < 50:
        time.sleep((50 - process_time) / 1000)  # sleep to maintain 50ms response time

    cv2.imshow("Img", img)
    if cv2.waitKey(1) & 0xFF == 27:  # Escape key to exit
        break

cap.release()
cv2.destroyAllWindows()
