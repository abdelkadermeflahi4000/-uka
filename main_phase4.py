from src.noosphere import Noosphere
from src.visualization import NoosphereVisualizer
from src.reality_simulator import RealityReSimulator
from src.genetic_engine import GeneticEngine

print("🌍 Đuka Protocol - Phase 4: Reality Re-simulation")

noosphere = Noosphere(num_agents=8, grid_size=20)
viz = NoosphereVisualizer(noosphere)
reality = RealityReSimulator(noosphere)

# Phase 4 Loop
for cycle in range(25):
    print(f"\nCycle {cycle} | Collective Reality: {noosphere.collective_reality_match():.4f}")
    
    for agent in noosphere.agents:
        env = agent.env
        obs, _ = env.reset()
        
        for step in range(120):
            action = agent.predict(obs, deterministic=True)
            obs, r, term, trunc, info = env.step(action)
            
            if step % 5 == 0:
                laser = agent.get_laser_action(obs)
                laser['frequency'] = 0.96  # تردد عالي لإعادة البرمجة
                env.add_laser_beam(**laser)
            
            if term or trunc or info['reality_match'] > 0.96:
                break
    
    noosphere.update_noosphere_field()
    noosphere.share_knowledge()
    
    # Reality Re-simulation كل 5 cycles
    if cycle % 5 == 0:
        reality.re_simulate(steps=30)
        viz.update(cycle)
        plt.pause(0.3)

print("🎯 Phase 4 مكتملة - الواقع أعيد برمجته!")
viz.animate()
