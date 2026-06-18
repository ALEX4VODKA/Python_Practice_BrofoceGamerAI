import cv2
import numpy as np
import mss

# 玩家模板
template = cv2.imread("player.png", 0)

w, h = template.shape[::-1]

monitor = {
    "top": 100,
    "left": 100,
    "width": 800,
    "height": 600
}

with mss.mss() as sct:

    while True:

        screenshot = sct.grab(monitor)

        frame = np.array(screenshot)

        gray = cv2.cvtColor(
            frame,
            cv2.COLOR_BGRA2GRAY
        )

        result = cv2.matchTemplate(
            gray,
            template,
            cv2.TM_CCOEFF_NORMED
        )

        _, max_val, _, max_loc = cv2.minMaxLoc(result)

        x, y = max_loc

        print("匹配度:", max_val)
        print("玩家位置:", x, y)

        cv2.rectangle(
            frame,
            (x, y),
            (x + w, y + h),
            (0, 255, 0),
            2
        )

        cv2.imshow("detect", frame)

        if cv2.waitKey(1) == ord('q'):
            break