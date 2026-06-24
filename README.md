# Broforce-RL

基于 PPO + OpenCV + Gymnasium 的 Broforce 游戏强化学习实验项目。

> 本项目旨在探索强化学习、计算机视觉与游戏 AI 在横版动作游戏中的应用。当前项目仍处于实验阶段，主要完成了环境搭建、视觉输入、动作控制、奖励设计等基础工作。

---

# 项目目标

训练一个 AI 玩家自动完成 Broforce 游戏中的：

* 向右推进
* 攻击敌人
* 跳跃避障
* 攀爬墙体
* 使用技能
* 生存与通关

最终目标是构建一个能够独立完成关卡的游戏 AI。

---

# 技术栈

## 强化学习

* PPO (Proximal Policy Optimization)
* Stable-Baselines3
* Gymnasium

## 计算机视觉

* OpenCV
* MSS Screen Capture
* Motion Detection

## 控制层

* PyAutoGUI

## 后续计划

* YOLOv8 目标检测
* DeepSeek 决策层
* Behavior Cloning 模仿学习
* 多智能体实验

---

# 当前实现

## 游戏环境封装

实现：

```text
Broforce
    ↓
Gymnasium Environment
    ↓
Stable-Baselines3 PPO
```

支持：

* reset()
* step()
* reward
* observation

---

## 屏幕捕获

使用 MSS 实时获取游戏画面：

```python
capture_screen()
```

分辨率：

```text
800 × 600
```

---

## 状态空间

当前采用：

```text
84 × 84 灰度图
```

并使用：

```text
Frame Stack = 4
```

最终 Observation：

```text
(4, 84, 84)
```

使 AI 具备时间序列感知能力。

---

## 动作空间

当前动作：

| ID | 动作   |
| -- | ---- |
| 0  | 无操作  |
| 1  | 向左   |
| 2  | 向右   |
| 3  | 跳跃   |
| 4  | 开枪   |
| 5  | 近战   |
| 6  | 右跳   |
| 7  | 左跳   |
| 8  | 右移射击 |
| 9  | 左移射击 |
| 10 | 右冲刺  |
| 11 | 技能   |

对应键位：

| 按键 | 功能 |
| -- | -- |
| W  | 跳跃 |
| A  | 左移 |
| D  | 右移 |
| G  | 开枪 |
| H  | 技能 |
| J  | 近战 |
| K  | 表情 |

---

# 已实现功能

## 1. Frame Stack

连续堆叠 4 帧画面：

```text
Frame t-3
Frame t-2
Frame t-1
Frame t
```

帮助 AI 理解：

* 运动方向
* 跳跃过程
* 子弹飞行
* 敌人移动

---

## 2. 推进奖励

根据角色横向位移给予奖励：

```python
progress = new_x - old_x
reward += progress
```

鼓励 AI 持续向右推进。

---

## 3. 死亡惩罚

检测死亡界面：

```python
is_dead()
```

给予负奖励：

```python
reward -= 5
```

---

## 4. 技能次数限制

技能键：

```text
H
```

当前限制：

```text
3次/局
```

防止 PPO 滥用技能。

---

## 5. 虚空检测（实验中）

目标：

识别地图空洞区域：

```text
前方无地面
```

触发：

```text
跳跃
```

当前效果不稳定。

---

## 6. 墙体检测（实验中）

目标：

识别：

```text
墙体
梯子
障碍
```

自动触发：

```text
攀爬
```

当前仍在调试。

---

## 7. 运动目标检测（实验中）

项目早期采用：

```text
OpenCV Template Matching
```

检测：

* soldier
* bomber
* dog
* boss
* bruiser

但由于：

* 动画变化
* 缩放问题
* 背景干扰

效果较差。

目前尝试改为：

```text
Motion Detection
```

即：

```text
识别所有运动物体
```

而不是识别具体敌人。

---

# 当前存在的问题

## 模板匹配不稳定

主要原因：

* 像素动画变化
* 多种敌人姿态
* 地图背景干扰

---

## Reward Engineering 复杂

目前仍在不断调整：

* 攻击奖励
* 跳跃奖励
* 生存奖励
* 推进奖励

容易出现：

```text
Reward Hacking
```

即：

AI 找到错误方式刷分。

---

## PPO 收敛缓慢

由于：

* 动作空间较大
* 场景复杂
* 视觉输入

训练需要：

```text
500k ~ 5M Timesteps
```

---

# 后续路线

## 第一阶段

完成：

* 稳定运动检测
* 虚空检测
* 墙体检测

---

## 第二阶段

接入：

YOLOv8

识别：

* 玩家
* 敌人
* 子弹
* 梯子
* 地形

---

## 第三阶段

接入：

DeepSeek

实现：

```text
视觉理解
↓
战术决策
↓
PPO执行
```

---

## 第四阶段

Behavior Cloning

录制真人操作：

```text
玩家操作
↓
模仿学习
↓
PPO微调
```

提高训练效率。

---

# 项目状态

当前状态：

```text
Research Prototype
实验原型
```

完成度：

约 40%

目前主要用于：

* 强化学习学习
* 游戏 AI 实验
* PPO 训练研究
* OpenCV 与 RL 结合探索

暂未达到自动通关水平。

---

# 致谢

感谢：

* Stable-Baselines3
* Gymnasium
* OpenCV
* MSS
* PyAutoGUI

以及所有开源强化学习社区提供的资料与案例。
