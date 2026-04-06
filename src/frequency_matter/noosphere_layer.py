"""🌐 NoosphereLayer - مجال وعي جماعي + إشارات تلوث/حالة نفسية
يقيس التماسك الطوري، الانتروبيا، ويكشف شذوذ "الوعي المعطوب".
"""
import torch
import numpy as np
from typing import List, Dict
import logging

logger = logging.getLogger("duka.noosphere")

class NoosphereField:
    def __init__(self, n_agents: int = 50, device: str = "cpu"):
        self.device = device
        self.agent_phases = torch.rand(n_agents, device=device) * 2 * np.pi
        self.pollution_signal = torch.zeros(1, device=device)
        self.mental_state_entropy = torch.zeros(1, device=device)
        
    def update(self, agent_phases: torch.Tensor, pollution_influx: float, stress_index: float):
        self.agent_phases = torch.remainder(agent_phases, 2*np.pi)
        self.pollution_signal = 0.95 * self.pollution_signal + 0.05 * pollution_influx
        # نموذج مبسط لانتروبيا الحالة النفسية
        phase_diffs = torch.remainder(self.agent_phases.unsqueeze(1) - self.agent_phases.unsqueeze(0), 2*np.pi)
        self.mental_state_entropy = -torch.mean(torch.log(phase_diffs / 2*np.pi + 1e-6)) + stress_index * 0.5
        
    def get_coherence(self) -> float:
        return torch.mean(torch.cos(self.agent_phases)).item()
        
    def get_anomaly_score(self) -> float:
        return (self.pollution_signal.item() * 0.6 + self.mental_state_entropy.item() * 0.4)
        
    def emit_resonance_pulse(self, intensity: float = 0.3):
        """دفعة ترابط جماعي (تقلل الانتروبيا مؤقتاً)"""
        mean_phase = torch.atan2(torch.mean(torch.sin(self.agent_phases)), torch.mean(torch.cos(self.agent_phases)))
        self.agent_phases = torch.lerp(self.agent_phases, mean_phase, intensity)
