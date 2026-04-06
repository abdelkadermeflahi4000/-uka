"""🌐 NoosphereField - حقل وعي جماعي مرجح بالتردد
يقيس التماسك الطوري، الانتروبيا، التلوث الترددي، ويولد نبضات رنين متزامنة
"""
import torch
import numpy as np
from typing import Dict, Tuple
import logging

logger = logging.getLogger("duka.noosphere")

class NoosphereField:
    def __init__(self, n_agents: int = 16, device: str = "cpu"):
        self.device = device
        self.n_agents = n_agents
        self.phases = torch.rand(n_agents, device=device) * 2 * np.pi
        self.coherence_buffer: list[float] = []
        self.pollution_level = torch.tensor(0.0, device=device)
        self.stress_index = torch.tensor(0.0, device=device)
        
        # حدود دستورية لمنع الانهيار الجماعي (hive-mind collapse)
        self.bounds = {"min_coherence": 0.15, "max_coherence": 0.88, "max_pollution": 0.7}

    def update(self, agent_phases: torch.Tensor, freq_drift: float, stress_signal: float):
        self.phases = torch.remainder(agent_phases, 2*np.pi)
        self.pollution_level = 0.94 * self.pollution_level + 0.06 * abs(freq_drift)
        self.stress_index = 0.92 * self.stress_index + 0.08 * stress_signal

    def compute_coherence(self) -> float:
        mean_vector = torch.mean(torch.exp(1j * self.phases))
        coh = torch.abs(mean_vector).item()
        self.coherence_buffer.append(coh)
        return max(self.bounds["min_coherence"], min(coh, self.bounds["max_coherence"]))

    def compute_entropy(self) -> float:
        if self.n_agents < 2: return 0.0
        diffs = torch.remainder(self.phases.unsqueeze(1) - self.phases.unsqueeze(0), 2*np.pi)
        norm_diffs = diffs / (2*np.pi) + 1e-8
        return -torch.mean(torch.log(norm_diffs)).item()

    def emit_resonance_pulse(self, intensity: float = 0.25) -> float:
        """نبضة رنين جماعي تُرفع التماسك مؤقتاً دون كسر الحدود الدستورية"""
        intensity = np.clip(intensity, 0.0, 0.4)
        mean_phase = torch.atan2(torch.mean(torch.sin(self.phases)), torch.mean(torch.cos(self.phases)))
        self.phases = torch.lerp(self.phases, mean_phase, intensity)
        return self.compute_coherence()

    def get_state(self) -> Dict:
        return {
            "coherence": self.compute_coherence(),
            "entropy": self.compute_entropy(),
            "pollution": self.pollution_level.item(),
            "stress": self.stress_index.item(),
            "trend": np.mean(self.coherence_buffer[-10:]) if self.coherence_buffer else 0.0
        }
