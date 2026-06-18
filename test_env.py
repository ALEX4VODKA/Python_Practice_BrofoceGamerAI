from broforce_env import BroforceEnv

env = BroforceEnv()

state, _ = env.reset()

print(state.shape)

env.step(2)