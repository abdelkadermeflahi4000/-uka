import numpy as np
from src.noosphere import Noosphere
from src.reality_simulator import RealityReSimulator
from src.visualization import NoosphereVisualizer
from src.hierarchical_world_model import HierarchicalWorldModel
from src.optimus_frequency_bridge import OptimusFrequencyBridge
from src.genetic_engine import GeneticEngine

class DukaOrchestrator:
    """
    النسخة النهائية المتكاملة - Phase 4.5
    """
    def __init__(self, num_agents=6, grid_size=24, use_optimus=True):
        print("🌌 Đuka Full Orchestrator with Optimus Integration")
        
        self.noosphere = Noosphere(num_agents=num_agents, grid_size=grid_size)
        self.reality = RealityReSimulator(self.noosphere)
        self.world_model = HierarchicalWorldModel(grid_size=grid_size)
        self.visualizer = NoosphereVisualizer(self.noosphere)
        
        # Optimus Bridge
        self.use_optimus = use_optimus
        if use_optimus:
            self.optimus = OptimusFrequencyBridge()
            print("🤖 Optimus Frequency Bridge Activated")
        
        self.cycle = 0
        self.global_reality_match = 0.0
    
    def run_cycle(self, steps_per_agent=120):
        self.cycle += 1
        print(f"\n🌍 Cycle {self.cycle} — Reality Programming + Optimus Modulation")
        
        for i, agent in enumerate(self.noosphere.agents):
            env = agent.env
            obs, _ = env.reset()
            
            for step in range(steps_per_agent):
                # Hierarchical Prediction
                pred_obs, _ = self.world_model(obs, agent.genome)
                
                # Agent Action
                action = agent.predict(obs, deterministic=True)
                obs, reward, term, trunc, info = env.step(action)
                
                # Laser Programming
                if step % 5 == 0:
                    laser = agent.get_laser_action(obs)
                    laser['frequency'] = 0.96 + 0.04 * self.global_reality_match
                    env.add_laser_beam(**laser)
                
                # === Optimus Frequency Bridge ===
                if self.use_optimus:
                    self.optimus.apply_frequency_field(
                        env.frequency_field,
                        self.noosphere.noosphere_field,
                        reality_match=info.get('reality_match', 0.85)
                    )
                    
                    # Laser effect on physical body
                    for beam in env.laser_beams[-3:]:  # آخر 3 أشعة
                        self.optimus.apply_laser_beam(beam)
                    
                    self.optimus.step_simulation(steps=6)
                
                if info['reality_match'] > 0.95:
                    break
        
        # Noosphere + Reality Updates
        self.noosphere.update_noosphere_field()
        self.noosphere.share_knowledge()
        self.reality.re_simulate(steps=35)
        
        self.global_reality_match = self.noosphere.collective_reality_match()
        
        # Visualization
        if self.cycle % 3 == 0:
            self.visualizer.update(self.cycle)
        
        return self.global_reality_match
    
    def run(self, max_cycles=60):
        for _ in range(max_cycles):
            match = self.run_cycle()
            print(f"🌟 Global Reality Match: {match:.4f}")
            if match > 0.965:
                print("🎯 Perfect Programmable Reality Achieved!")
                break
        if self.use_optimus:
            print("🤖 Optimus simulation finished")
        self.visualizer.animate()
