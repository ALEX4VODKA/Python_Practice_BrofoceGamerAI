import cv2
import numpy as np
import mss

# 读取死亡模板
template = cv2.imread("death.png", 0)

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

        _, max_val, _, _ = cv2.minMaxLoc(result)

        print("匹配度:", max_val)

        if max_val > 0.8:
            print("角色死亡")

        cv2.imshow("game", gray)

        if cv2.waitKey(1) == ord('q'):
            break