import numpy as np
from typing import List, Dict, Optional
from src.agent import LaserGeneticAgent
from src.environment import FrequencyGridWorld

class Noosphere:
    """
    Noosphere Layer - Phase 2
    الوعي الجماعي: شبكة من الـ LaserGeneticAgents
    يتأثر بالتلوث + الأمراض النفسية + الهندسة الوراثية
    """
    
    def __init__(self, num_agents: int = 8, grid_size: int = 12):
        self.num_agents = num_agents
        self.grid_size = grid_size
        self.agents: List[LaserGeneticAgent] = []
        self.noosphere_field = np.zeros((grid_size, grid_size), dtype=np.float32)  # حقل الوعي الجماعي
        self.pollution_field = np.random.uniform(0.0, 0.4, (grid_size, grid_size))  # تلوث أرضي/نفسي
        self.mental_disorder_map = np.zeros((grid_size, grid_size))  # أمراض نفسية
        
        # إنشاء الـ Agents
        self.envs = [FrequencyGridWorld(grid_size=grid_size) for _ in range(num_agents)]
        for i in range(num_agents):
            agent = LaserGeneticAgent(self.envs[i])
            # جينوم وراثي مختلف قليلاً لكل agent
            agent.genome[32:40] += np.random.normal(0, 0.1, 8)  # تنوع جيني
            self.agents.append(agent)
        
        print(f"🌐 Noosphere initialized with {num_agents} conscious nodes")
    
    def update_noosphere_field(self):
        """دمج الوعي من كل الـ agents"""
        self.noosphere_field.fill(0.0)
        for agent in self.agents:
            # كل agent يضيف تردده + reality match
            pos = agent.env.agent_pos
            influence = agent.genome[24:32].mean()  # قوة وعيه
            self.noosphere_field[pos[0], pos[1]] += influence * 0.8
        
        # انتشار الوعي (diffusion)
        self.noosphere_field = self._diffuse_field(self.noosphere_field, diffusion_rate=0.25)
        
        # تأثير التلوث والأمراض
        self.noosphere_field -= self.pollution_field * 0.6
        self.noosphere_field -= self.mental_disorder_map * 0.4
        self.noosphere_field = np.clip(self.noosphere_field, -1.0, 1.0)
    
    def _diffuse_field(self, field: np.ndarray, diffusion_rate: float = 0.2) -> np.ndarray:
        """انتشار الوعي / التلوث"""
        new_field = field.copy()
        for _ in range(2):  # iterations
            new_field = new_field * (1 - diffusion_rate) + \
                       diffusion_rate * 0.25 * (
                           np.roll(field, 1, axis=0) + np.roll(field, -1, axis=0) +
                           np.roll(field, 1, axis=1) + np.roll(field, -1, axis=1)
                       )
        return new_field
    
    def inject_mental_disorder(self, pos: tuple, intensity: float = 0.8, radius: int = 2):
        """حقن مرض نفسي في الـ Noosphere"""
        x, y = pos
        for i in range(-radius, radius+1):
            for j in range(-radius, radius+1):
                if 0 <= x+i < self.grid_size and 0 <= y+j < self.grid_size:
                    dist = max(abs(i), abs(j))
                    self.mental_disorder_map[x+i, y+j] = max(
                        self.mental_disorder_map[x+i, y+j],
                        intensity * (1 - dist/(radius+1))
                    )
    
    def inject_pollution(self, pos: tuple, intensity: float = 0.7):
        """تلوث بيئي/نفسي"""
        x, y = pos
        self.pollution_field[x, y] = min(1.0, self.pollution_field[x, y] + intensity)
    
    def collective_reality_match(self) -> float:
        """متوسط Reality Match الجماعي"""
        return np.mean([a.genome[24:32].mean() for a in self.agents])
    
    def share_knowledge(self):
        """تبادل معرفة (Knowledge Sharing عبر Noosphere)"""
        # Averaging genomes (بداية Federated Learning بسيط)
        avg_genome = np.mean([a.genome for a in self.agents], axis=0)
        for agent in self.agents:
            agent.genome = 0.7 * agent.genome + 0.3 * avg_genome
            # Mutation خفيفة للتنوع
            agent.genome += np.random.normal(0, 0.03, len(agent.genome))
