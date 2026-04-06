"""🧬 Genetic Collective Sync - تطور موزع مرجح بالرنين
يتبادل الشظايا الجينية عبر العقد، يزن التزاوج بالتماسك، ويكيّف الطفرة حسب الإجهاد
"""
import numpy as np
from typing import List, Dict, Optional
from dataclasses import dataclass
import time
import logging

logger = logging.getLogger("duka.genetic_collective")

@dataclass
class GenomeFragment:
    node_id: str
    genes: np.ndarray
    fitness: float
    coherence: float
    timestamp: float

class GeneticCollectiveManager:
    def __init__(self, constitutional_rules: Dict, genome_dim: int = 32):
        self.rules = constitutional_rules
        self.dim = genome_dim
        self.pool: List[GenomeFragment] = []
        self.sync_interval = self.rules.get("sync_interval", 50)
        self.step = 0
        self.last_sync_time = 0.0

    def submit_fragment(self, frag: GenomeFragment):
        self.pool.append(frag)
        if len(self.pool) > 16:
            self.pool.pop(0)

    def sync_and_evolve(self, local_genome: np.ndarray, local_fitness: float, 
                        local_coherence: float) -> np.ndarray:
        self.step += 1
        if self.step % self.sync_interval != 0 or len(self.pool) < 2:
            return local_genome

        # 1. ترجيح بالرنين + اللياقة
        weights = np.array([f.coherence * f.fitness for f in self.pool])
        weights = np.exp(weights) / (np.sum(np.exp(weights)) + 1e-8)
        
        # 2. اختيار آباء
        idx = np.random.choice(len(self.pool), size=2, p=weights, replace=False)
        p1, p2 = self.pool[idx[0]], self.pool[idx[1]]

        # 3. تزاوج موجه للجينات الليزرية (4-15)
        child = local_genome.copy()
        mask = np.zeros(self.dim, dtype=bool)
        mask[4:16] = True
        crossover_pt = np.random.randint(4, 16)
        mask[crossover_pt:] = False
        
        child[mask] = p1.genes[mask] * 0.6 + p2.genes[mask] * 0.4
        
        # 4. طفرة متكيفة مع الإجهاد/التلوث
        stress_factor = 1.0 - local_coherence
        mut_rate = self.rules.get("base_mut", 0.06) * (1.0 + 1.5 * stress_factor)
        mut_mask = np.random.random(self.dim) < mut_rate
        child[mut_mask] += np.random.randn(mut_mask.sum()) * 0.04
        child = np.clip(child, -1.0, 1.0)

        # 5. تحقق دستوري سريع
        if not self._validate_constitutional(child):
            return local_genome

        self.pool.clear()
        self.last_sync_time = time.time()
        return child

    def _validate_constitutional(self, genome: np.ndarray) -> bool:
        # منع التطرف الليزري أو الانهيار الجيني
        if np.mean(np.abs(genome[4:16])) > 0.85: return False
        if np.std(genome) > 0.75: return False
        if np.any(genome[15] > 0.95): return False  # stealth cutoff bound
        return True
