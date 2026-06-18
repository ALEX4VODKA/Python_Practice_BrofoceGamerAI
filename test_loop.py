from broforce_env import BroforceEnv
import random

env = BroforceEnv()

state, _ = env.reset()

while True:

    action = random.randint(0, 5)

    state, reward, done, _, _ = env.step(action)

    print(reward, done)

    if done:

        print("重新开始")

        state, _ = env.reset()