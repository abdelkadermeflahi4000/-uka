from src.environment import FrequencyGridWorld
from src.agent import LaserGeneticAgent
from src.noosphere import Noosphere
from src.visualization import NoosphereVisualizer
from src.hierarchical_world_model import HierarchicalWorldModel
from src.genetic_engine import GeneticEngine

print("🚀 Đuka Protocol - Phase 3 Started")

noosphere = Noosphere(num_agents=6, grid_size=16)
world_model = HierarchicalWorldModel(grid_size=16)
viz = NoosphereVisualizer(noosphere)

# Phase 3: Programmable Time + Matter
for episode in range(40):
    print(f"\n=== Episode {episode} | Collective Reality: {noosphere.collective_reality_match():.4f} ===")
    
    for agent in noosphere.agents:
        env = agent.env
        obs, _ = env.reset()
        
        for step in range(100):
            # Hierarchical Prediction
            pred_obs, time_error = world_model(obs, agent.genome)
            
            # Agent يتخذ قرار بناءً على التنبؤ
            action = agent.predict(obs)
            obs, reward, term, trunc, info = env.step(action)
            
            # Programmable Matter via Laser
            if step % 6 == 0:
                laser = agent.get_laser_action(obs)
                laser['frequency'] += 0.1 * (1 - time_error)  # يعدل حسب التنبؤ
                env.add_laser_beam(**laser)
            
            # Reality becomes programmable
            if info['reality_match'] > 0.85:
                # Time dilation
                env.time_field *= 0.98  # إبطاء/تسريع الزمن
            
            if term or trunc:
                break
    
    noosphere.update_noosphere_field()
    noosphere.share_knowledge()
    
    # Visualization every 5 episodes
    if episode % 5 == 0:
        viz.update(episode)
        plt.pause(0.1)

print("🎯 Phase 3 Complete - Programmable Time & Matter Activated!")
viz.animate()  # تشغيل الـ animation في النهاية
