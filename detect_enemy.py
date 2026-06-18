import cv2
import numpy as np
import mss

# =========================
# 读取模板
# =========================
template = cv2.imread(
    "enemies/soldier.png",
    0
)

# 检查是否读取成功
if template is None:

    print("模板读取失败！")
    exit()

print("模板尺寸:", template.shape)

# 显示模板
cv2.imshow(
    "template",
    template
)

cv2.waitKey(1000)

# =========================
# 游戏区域
# =========================
monitor = {
    "top": 100,
    "left": 100,
    "width": 800,
    "height": 600
}

# =========================
# 开始检测
# =========================
with mss.mss() as sct:

    while True:

        screenshot = sct.grab(
            monitor
        )

        frame = np.array(
            screenshot
        )

        gray = cv2.cvtColor(
            frame,
            cv2.COLOR_BGRA2GRAY
        )

        result = cv2.matchTemplate(
            gray,
            template,
            cv2.TM_CCOEFF_NORMED
        )

        # 最高匹配值
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(
            result
        )

        print("最高匹配值:", max_val)

        threshold = 0.7

        if max_val >= threshold:

            w, h = template.shape[::-1]

            top_left = max_loc

            bottom_right = (
                top_left[0] + w,
                top_left[1] + h
            )

            cv2.rectangle(
                frame,
                top_left,
                bottom_right,
                (0, 0, 255),
                2
            )

        cv2.imshow(
            "detect",
            frame
        )

        if cv2.waitKey(1) == ord('q'):
            break

cv2.destroyAllWindows()