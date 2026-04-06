from src.environment import FrequencyGridWorld
from src.noosphere import Noosphere
from src.optimus_frequency_bridge import OptimusFrequencyBridge

print("🚀 Optimus Frequency Test Started")

env = FrequencyGridWorld(grid_size=16)
noosphere = Noosphere(num_agents=4, grid_size=16)
bridge = OptimusFrequencyBridge()

for episode in range(30):
    obs, _ = env.reset()
    print(f"Episode {episode} | Reality Match: {noosphere.collective_reality_match():.3f}")
    
    for step in range(80):
        action = np.random.randint(0, 5)
        obs, _, _, _, info = env.step(action)
        
        if step % 6 == 0:
            laser = {"start": (3,3), "direction": (1,1), "frequency": 0.95, "amp": 1.0}
            env.add_laser_beam(**laser)
        
        # ربط بالروبوت
        bridge.apply_frequency_field(env.frequency_field, 
                                   noosphere.noosphere_field,
                                   reality_match=info.get("reality_match", 0.8))
        
        for beam in env.laser_beams:
            bridge.apply_laser_beam(beam)
        
        bridge.step_simulation(steps=8)
    
    noosphere.update_noosphere_field()
    noosphere.share_knowledge()

print("✅ Test completed - Optimus modulated by frequencies!")
p.disconnect()
