"""🧬 GeneticAgent - وكيل مشفر جينياً يتطور ذاتياً داخل الحلقة الترددية"""
import torch
import numpy as np
from typing import Dict, Optional
import logging

logger = logging.getLogger("duka.genetic")

class Genome:
    def __init__(self, dim: int = 32):
        self.vector = torch.randn(dim)
        self.fitness = 0.0
        self.age = 0
        
    def mutate(self, rate: float = 0.05, scale: float = 0.1):
        mask = torch.rand_like(self.vector) < rate
        self.vector[mask] += torch.randn_like(self.vector[mask]) * scale
        self.vector = torch.clamp(self.vector, -2.0, 2.0)
        self.age += 1
        
    @classmethod
    def crossover(cls, g1: "Genome", g2: "Genome"):
        child = Genome(dim=len(g1.vector))
        cut = np.random.randint(1, len(g1.vector)-1)
        child.vector[:cut] = g1.vector[:cut]
        child.vector[cut:] = g2.vector[cut:]
        return child

class GeneticAgent:
    def __init__(self, genome: Optional[Genome] = None, device: str = "cpu"):
        self.genome = genome or Genome(32)
        self.device = device
        self.policy_head = torch.nn.Sequential(
            torch.nn.Linear(32, 64), torch.nn.GELU(), torch.nn.Linear(64, 7)
        ).to(device)
        
    def act(self, obs: Dict) -> Dict:
        # دمج الملاحظة مع الجينوم → قرار
        flat_obs = torch.cat([
            torch.tensor(obs["agent_pos"], dtype=torch.float32),
            torch.tensor(obs["field_amp"].mean(axis=(1,2))),
            torch.tensor(obs["field_phase"].mean(axis=(1,2)))
        ]).to(self.device)
        
        x = torch.cat([flat_obs, self.genome.vector.to(self.device)])
        logits = self.policy_head(x)
        return {
            "move": torch.argmax(logits[:5]).item(),
            "emit_band": torch.argmax(logits[5:5+3]).item(),
            "morph": torch.sigmoid(logits[7:]).tolist()
        }
    
    def update_fitness(self, reward: float):
        self.genome.fitness = 0.9 * self.genome.fitness + 0.1 * reward
        
    def reproduce_with(self, other: "GeneticAgent", mutation_rate: float = 0.05):
        child_genome = Genome.crossover(self.genome, other.genome)
        child_genome.mutate(rate=mutation_rate)
        return GeneticAgent(child_genome, self.device)
