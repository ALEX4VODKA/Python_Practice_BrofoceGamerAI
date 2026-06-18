import gymnasium as gym
from gymnasium import spaces

import numpy as np
import cv2
import mss
import pyautogui
import time
import os

from collections import deque


class BroforceEnv(gym.Env):

    def __init__(self):

        super().__init__()

        # =========================
        # Frame Stack
        # =========================
        self.frames = deque(maxlen=4)

        # =========================
        # PPO 动作空间
        # =========================
        self.action_space = spaces.Discrete(12)

        self.skill_count = 3
        # =========================
        # PPO 状态空间
        # =========================
        self.observation_space = spaces.Box(
            low=0,
            high=255,
            shape=(4, 84, 84),
            dtype=np.uint8
        )

        # =========================
        # 多敌人模板
        # =========================
        self.enemy_templates = {}

        enemy_folder = "enemies"

        for file in os.listdir(enemy_folder):

            path = os.path.join(
                enemy_folder,
                file
            )

            template = cv2.imread(path, 0)

            if template is not None:

                enemy_name = file.replace(
                    ".png",
                    ""
                ).lower()

                self.enemy_templates[
                    enemy_name
                ] = template

        print("已加载敌人模板:")

        for name in self.enemy_templates:
            print(name)

        # =========================
        # 玩家模板
        # =========================
        self.player_template = cv2.imread(
            "p1.png",
            0
        )

        # =========================
        # 死亡模板
        # =========================
        self.death_template = cv2.imread(
            "death.png",
            0
        )

        # =========================
        # 上一帧敌人数
        # =========================
        self.last_enemy_count = 0

        # =========================
        # 游戏截图区域
        # =========================
        self.monitor = {
            "top": 100,
            "left": 100,
            "width": 800,
            "height": 600
        }

    # ==================================================
    # RESET
    # ==================================================
    def reset(self, seed=None, options=None):

        super().reset(seed=seed)

        pyautogui.press('space')

        time.sleep(2)

        frame_full = self.capture_screen()

        frame_small = self.process_state(
            frame_full
        )

        self.frames.clear()

        self.last_enemy_count = 0
        self.skill_count = 3
        state = self.stack_frames(
            frame_small
        )

        return state, {}

    # ==================================================
    # STEP
    # ==================================================
    def step(self, action):

        # 防止卡键
        pyautogui.keyUp('a')
        pyautogui.keyUp('d')

        # 玩家旧位置
        old_x, old_y = self.get_player_position()

        # 执行动作
        self.do_action(action)

        time.sleep(0.05)

        # 截图
        frame_full = self.capture_screen()

        # 状态图
        frame_small = self.process_state(
            frame_full
        )

        state = self.stack_frames(
            frame_small
        )

        # 玩家新位置
        new_x, new_y = self.get_player_position(
            frame_full
        )

        wall_near = self.detect_wall(
            frame_full,
            new_x,
            new_y
        )

        is_void = self.detect_void(
            frame_full,
            new_x,
            new_y
        )

        # 敌人检测
        motions = self.detect_motion(
            frame_full
        )
        enemy_count = len(motions)

        current_enemy_count = len(motions)

        # 死亡检测
        done = self.is_dead(
            frame_full
        )

        no_enemy = len(motions) == 0

        # ==================================================
        # Reward
        # ==================================================

        # 推进奖励
        progress = max(
            min(new_x - old_x, 5),
            -5
        )

        reward = progress * 0.2

        # 没敌人时
        if no_enemy:

            # 鼓励右移动
            if action in [2, 8]:
                reward += 0.1

            # 鼓励右冲刺
            if action == 10:
                reward += 0.2
        # 不动惩罚
        if abs(progress) < 1:
            reward -= 0.05

        # 向右偏好
        if action in [2, 6, 8]:
            reward += 0.03

        # 跳跃惩罚
        if action == 3:
            reward -= 0.02

        # 攀爬跳惩罚
        if action in [6, 7]:
            reward -= 0.01

        if wall_near:

            # 鼓励右跳攀爬
            if action == 6:
                reward += 0.3

        if is_void:

            # 鼓励跳跃
            if action in [3, 6]:
                reward += 0.4

            # 掉坑倾向
            if action in [0, 2, 10]:
                reward -= 0.3

        if action == 11:
            if self.skill_count > 0:

                reward += 0.1

                self.skill_count -= 1

            else:

                reward -= 0.5
        # ==================================================
        # 多敌人战斗奖励
        # ==================================================
        for x, y, w, h in motions:

            distance_x = x - new_x
            distance_y = y - new_y

            # 水平附近
            if abs(distance_y) < 80:

                # 射击奖励
                if action in [4, 8, 9]:
                    reward += 0.03

                # 技能奖励
                if action == 11:

                    if abs(distance_x) < 120:
                        reward += 0.05

                # 近战
                if action == 5:

                    if abs(distance_x) < 30:
                        reward += 0.08

                    else:
                        reward -= 0.15

        # ==================================================
        # 击杀奖励
        # ==================================================
        if current_enemy_count < self.last_enemy_count:

            killed = (
                self.last_enemy_count
                - current_enemy_count
            )

            reward += killed * 1.0

        # 更新敌人数
        self.last_enemy_count = current_enemy_count

        # 死亡惩罚
        if done:
            reward -= 5

        reward = float(reward)

        return state, reward, done, False, {}

    # ==================================================
    # 动作执行
    # ==================================================
    def do_action(self, action):

        if action == 0:
            pass

        elif action == 1:
            pyautogui.press('a')

        elif action == 2:
            pyautogui.press('d')

        elif action == 3:
            pyautogui.press('w')

        elif action == 4:
            pyautogui.press('g')

        elif action == 5:
            pyautogui.press('j')

        # 右跳（攀爬）
        elif action == 6:

            pyautogui.keyDown('d')
            pyautogui.press('w')
            pyautogui.keyUp('d')

        # 左跳（攀爬）
        elif action == 7:

            pyautogui.keyDown('a')
            pyautogui.press('w')
            pyautogui.keyUp('a')

        # 右移射击
        elif action == 8:

            pyautogui.keyDown('d')
            pyautogui.press('g')
            pyautogui.keyUp('d')

        # 左移射击
        elif action == 9:

            pyautogui.keyDown('a')
            pyautogui.press('g')
            pyautogui.keyUp('a')

        # 右冲刺
        elif action == 10:

            pyautogui.press('d')
            time.sleep(0.03)
            pyautogui.press('d')

        # 技能
        elif action == 11:

            pyautogui.press('h')

    # ==================================================
    # 截图
    # ==================================================
    def capture_screen(self):

        with mss.mss() as sct:

            screenshot = sct.grab(
                self.monitor
            )

            frame = np.array(
                screenshot
            )

            return frame

    # ==================================================
    # 状态处理
    # ==================================================
    def process_state(self, frame):

        gray = cv2.cvtColor(
            frame,
            cv2.COLOR_BGRA2GRAY
        )

        small = cv2.resize(
            gray,
            (84, 84)
        )

        return small.astype(np.uint8)

    # ==================================================
    # Frame Stack
    # ==================================================
    def stack_frames(self, frame):

        if frame is None:

            frame = np.zeros(
                (84, 84),
                dtype=np.uint8
            )

        self.frames.append(frame)

        while len(self.frames) < 4:
            self.frames.append(frame)

        stacked = np.stack(
            self.frames,
            axis=0
        )

        return stacked.astype(np.uint8)

    # ==================================================
    # 玩家检测
    # ==================================================
    def get_player_position(self, frame=None):

        if self.player_template is None:
            return 0, 0

        if frame is None:
            frame = self.capture_screen()

        gray = cv2.cvtColor(
            frame,
            cv2.COLOR_BGRA2GRAY
        )

        result = cv2.matchTemplate(
            gray,
            self.player_template,
            cv2.TM_CCOEFF_NORMED
        )

        _, max_val, _, max_loc = cv2.minMaxLoc(
            result
        )

        if max_val < 0.5:
            return 0, 0

        x, y = max_loc

        return x, y

    # ==================================================
    # 多敌人检测
    # ==================================================
    def detect_enemy(self, frame):

        gray = cv2.cvtColor(
            frame,
            cv2.COLOR_BGRA2GRAY
        )

        enemies = []

        for enemy_name, template in self.enemy_templates.items():

            w, h = template.shape[::-1]

            result = cv2.matchTemplate(
                gray,
                template,
                cv2.TM_CCOEFF_NORMED
            )

            threshold = 0.72

            locations = np.where(
                result >= threshold
            )

            for pt in zip(*locations[::-1]):

                enemy_x = pt[0]
                enemy_y = pt[1]

                # 去重
                too_close = False

                for _, ex, ey in enemies:

                    if (
                        abs(enemy_x - ex) < 25
                        and
                        abs(enemy_y - ey) < 25
                    ):

                        too_close = True
                        break

                if not too_close:

                    enemies.append(
                        (
                            enemy_name,
                            enemy_x,
                            enemy_y
                        )
                    )

        return enemies

    # ==================================================
    # 死亡检测
    # ==================================================
    def is_dead(self, frame):

        if self.death_template is None:
            return False

        gray = cv2.cvtColor(
            frame,
            cv2.COLOR_BGRA2GRAY
        )

        result = cv2.matchTemplate(
            gray,
            self.death_template,
            cv2.TM_CCOEFF_NORMED
        )

        _, max_val, _, _ = cv2.minMaxLoc(
            result
        )

        return max_val > 0.8

    def detect_void(self, frame, player_x, player_y):

        # 玩家前方脚下区域
        x1 = min(player_x + 60, 760)
        y1 = min(player_y + 80, 560)

        x2 = min(x1 + 40, 799)
        y2 = min(y1 + 40, 599)

        area = frame[
            y1:y2,
            x1:x2
        ]

        if area.size == 0:
            return False

        # 转 HSV
        hsv = cv2.cvtColor(
            area,
            cv2.COLOR_BGR2HSV
        )

        # 蓝色范围
        lower_blue = np.array(
            [90, 50, 50]
        )

        upper_blue = np.array(
            [130, 255, 255]
        )

        mask = cv2.inRange(
            hsv,
            lower_blue,
            upper_blue
        )

        blue_ratio = (
                np.sum(mask > 0)
                / mask.size
        )

        return blue_ratio > 0.6

    def detect_wall(self, frame, player_x, player_y):

        x1 = min(player_x + 40, 760)
        y1 = max(player_y, 0)

        x2 = min(x1 + 30, 799)
        y2 = min(y1 + 80, 599)

        area = frame[
            y1:y2,
            x1:x2
        ]

        if area.size == 0:
            return False

        gray = cv2.cvtColor(
            area,
            cv2.COLOR_BGR2GRAY
        )

        darkness = np.mean(gray)

        return darkness < 70

    def detect_motion(self, frame):

        gray = cv2.cvtColor(
            frame,
            cv2.COLOR_BGRA2GRAY
        )

        # 第一帧
        if not hasattr(self, "last_gray"):
            self.last_gray = gray

            return []

        # 帧差
        diff = cv2.absdiff(
            self.last_gray,
            gray
        )

        self.last_gray = gray

        # 二值化
        _, thresh = cv2.threshold(
            diff,
            25,
            255,
            cv2.THRESH_BINARY
        )

        # 膨胀
        kernel = np.ones(
            (3, 3),
            np.uint8
        )

        thresh = cv2.dilate(
            thresh,
            kernel,
            iterations=2
        )

        # 查找轮廓
        contours, _ = cv2.findContours(
            thresh,
            cv2.RETR_EXTERNAL,
            cv2.CHAIN_APPROX_SIMPLE
        )

        motions = []

        for contour in contours:

            area = cv2.contourArea(
                contour
            )

            # 太小忽略
            if area < 80:
                continue

            x, y, w, h = cv2.boundingRect(
                contour
            )
            # 忽略玩家附近
            screen_center_x = 400

            if abs(x - screen_center_x) < 80:
                continue
            motions.append(
                (
                    x,
                    y,
                    w,
                    h
                )
            )

        return motions