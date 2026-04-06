import numpy as np      # ✅ FIX: كان مفقوداً — np.random.rand() يرفع NameError
from src.environment import FrequencyGridWorld
from src.agent import LaserGeneticAgent

env = FrequencyGridWorld(grid_size=12)
agent = LaserGeneticAgent(env)

# تدريب
agent.learn(total_timesteps=80000)

# اختبار
obs, _ = env.reset()
for step in range(200):
    action = agent.predict(obs, deterministic=True)
    obs, reward, terminated, truncated, info = env.step(action)

    # الـ Agent يقرر إطلاق ليزر بنفسه
    if step % 8 == 0 and np.random.rand() < 0.7:   # ✅ np يعمل الآن
        laser_params = agent.get_laser_action(obs)
        env.add_laser_beam(**laser_params)

    env.render()
    print(f"Reality Match: {info['reality_match']:.4f} | Lasers: {info['lasers_active']}")

    if terminated or truncated:
        print("🎯 الحلقة انتهت - Reality Match:", info['reality_match'])
        break
