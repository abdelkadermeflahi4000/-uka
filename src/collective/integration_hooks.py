"""🔗 Integration Hooks - توصيل Noosphere + GeneticCollective بالحلقة الحالية"""
import torch
import numpy as np
from typing import Dict, Tuple
import logging

logger = logging.getLogger("duka.collective_integration")

class CollectiveIntegrationHook:
    def __init__(self, n_agents: int = 16, device: str = "cpu", constitutional_rules: Dict = None):
        self.noosphere = NoosphereField(n_agents=n_agents, device=device)
        self.collective = GeneticCollectiveManager(
            constitutional_rules or {"sync_interval": 50, "base_mut": 0.06},
            genome_dim=32
        )
        self.device = device

    def step_hook(self, agent_phases: np.ndarray, pred_freq: np.ndarray, 
                  pred_time: np.ndarray, local_genome: np.ndarray, 
                  local_fitness: float, stress_index: float) -> Tuple[np.ndarray, Dict]:
        """يُستدعى داخل GeneticLaserWrapper.step() بعد التنبؤ"""
        # 1. تحديث Noosphere
        phases_t = torch.tensor(agent_phases, device=self.device)
        freq_drift = float(np.std(pred_freq))
        self.noosphere.update(phases_t, freq_drift, stress_index)
        
        noo_state = self.noosphere.get_state()
        
        # 2. نبضة رنين تلقائية إذا انخفض التماسك
        if noo_state["coherence"] < 0.25:
            self.noosphere.emit_resonance_pulse(intensity=0.3)
            noo_state["coherence"] = self.noosphere.compute_coherence()
            noo_state["pulse_emitted"] = True
        else:
            noo_state["pulse_emitted"] = False

        # 3. إرسال شظية جينية للبركة
        self.collective.submit_fragment(GenomeFragment(
            node_id="local", genes=local_genome.copy(),
            fitness=local_fitness, coherence=noo_state["coherence"],
            timestamp=noo_state["trend"]
        ))

        # 4. مزامنة وتطور جماعي
        evolved_genome = self.collective.sync_and_evolve(
            local_genome, local_fitness, noo_state["coherence"]
        )

        return evolved_genome, noo_state
