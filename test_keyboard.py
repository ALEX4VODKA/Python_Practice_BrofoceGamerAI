import time
import pyautogui

print("5秒后开始")
time.sleep(5)

# 向右移动2秒
pyautogui.keyDown('w')

time.sleep(2)

pyautogui.keyUp('w')

print("结束")