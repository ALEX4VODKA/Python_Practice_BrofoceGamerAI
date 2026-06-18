from stable_baselines3 import PPO
from broforce_env import BroforceEnv

env = BroforceEnv()

model = PPO(
    "CnnPolicy",
    env,
    verbose=1
)

model.learn(
    total_timesteps=10000
)

model.save("bgAGagawroforce_ppo")