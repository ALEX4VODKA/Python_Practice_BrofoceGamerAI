from stable_baselines3 import PPO
from broforce_env import BroforceEnv

env = BroforceEnv()

model = PPO.load("broforce_ppo")

state, _ = env.reset()

while True:

    action, _ = model.predict(state)

    state, reward, done, _, _ = env.step(action)

    if done:
        state, _ = env.reset()