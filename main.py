from src.environment import FrequencyGridWorld
from src.agent import DukaAgent  # سنحدثه بعدين

env = FrequencyGridWorld(grid_size=12, render_mode="human")

obs, _ = env.reset()

# إطلاق أشعة ليزر صامتة
env.add_laser_beam(start=(3,3), direction=(1,1), frequency=0.95, is_silent=True)
env.add_laser_beam(start=(8,4), direction=(-1,0.5), frequency=0.88, is_silent=True)

for _ in range(50):
    action = env.action_space.sample()   # أو action من agent
    obs, reward, term, trunc, info = env.step(action)
    env.render()
    if term or trunc:
        break
