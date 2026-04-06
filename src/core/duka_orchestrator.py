import numpy as np
from src.noosphere import Noosphere
from src.reality_simulator import RealityReSimulator
from src.visualization import NoosphereVisualizer
from src.hierarchical_world_model import HierarchicalWorldModel
from src.genetic_engine import GeneticEngine

class DukaOrchestrator:
    """
    Đuka Protocol - Full Integration Engine
    يربط كل الطبقات: Frequency → Laser → Noosphere → Reality Re-simulation
    """
    def __init__(self, num_agents=8, grid_size=24):
        print("🌌 Initializing Đuka Full Integration...")
        
        self.noosphere = Noosphere(num_agents=num_agents, grid_size=grid_size)
        self.reality = RealityReSimulator(self.noosphere)
        self.world_model = HierarchicalWorldModel(grid_size=grid_size)
        self.visualizer = NoosphereVisualizer(self.noosphere)
        
        self.cycle = 0
        self.global_reality_match = 0.0
    
    def run_cycle(self, steps_per_agent=150):
        """دورة كاملة من البرمجة إلى إعادة المحاكاة"""
        self.cycle += 1
        print(f"\n🌍 Cycle {self.cycle} - Full Reality Programming")
        
        for agent in self.noosphere.agents:
            env = agent.env
            obs, _ = env.reset()
            
            for step in range(steps_per_agent):
                # Hierarchical Prediction
                pred, _ = self.world_model(obs, agent.genome)
                
                # Action + Laser Programming
                action = agent.predict(obs, deterministic=True)
                obs, reward, term, trunc, info = env.step(action)
                
                if step % 4 == 0:
                    laser = agent.get_laser_action(obs)
                    laser['frequency'] = 0.97 + 0.03 * self.global_reality_match
                    env.add_laser_beam(**laser)
                
                if info['reality_match'] > 0.94:
                    break
        
        # Noosphere Evolution
        self.noosphere.update_noosphere_field()
        self.noosphere.share_knowledge()
        
        # Reality Re-simulation
        self.reality.re_simulate(steps=40)
        
        # Update global state
        self.global_reality_match = self.noosphere.collective_reality_match()
        
        # Live Visualization
        if self.cycle % 3 == 0:
            self.visualizer.update(self.cycle)
        
        return self.global_reality_match
    
    def run(self, max_cycles=50):
        """تشغيل النظام الكامل"""
        print("🚀 Đuka Protocol Full Integration Started")
        for _ in range(max_cycles):
            match = self.run_cycle()
            if match > 0.96:
                print("🎯 Perfect Reality Achieved - System Stable")
                break
        self.visualizer.animate()
