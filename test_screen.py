import cv2
import numpy as np
import mss

monitor = {
    "top": 50,
    "left": 0,
    "width": 1000,
    "height":750
}

with mss.mss() as sct:

    while True:

        screenshot = sct.grab(monitor)

        frame = np.array(screenshot)

        frame = cv2.cvtColor(
            frame,
            cv2.COLOR_BGRA2BGR
        )

        cv2.imshow("Broforce", frame)

        if cv2.waitKey(1) == ord('q'):
            break

cv2.destroyAllWindows()