import numpy as np
from typing import Dict


class NodeBrain:
    """وعي فردي داخل كل عقدة Đuka (LaserGeneticAgent أو Noosphere node)"""
    def __init__(self, node_id: str, n_osc: int = 32, base_freq: float = 7.83):
        self.node_id = node_id
        self.n_osc = n_osc
        self.phase = np.random.uniform(0, 2 * np.pi, n_osc)
        self.freq = np.random.normal(base_freq, 0.5, n_osc)   # تردد شومان + تنوّع
        self.coherence_history: list[float] = []

    def step(self, dt: float = 0.033):  # 30Hz
        self.phase = (self.phase + dt * self.freq) % (2 * np.pi)
        coh = self.coherence()
        self.coherence_history.append(coh)
        if len(self.coherence_history) > 100:
            self.coherence_history.pop(0)

    def coherence(self) -> float:
        return float(np.abs(np.mean(np.exp(1j * self.phase))))

    def state(self) -> Dict:
        return {
            "id": self.node_id,
            "phase": self.phase.tolist(),
            "coherence": self.coherence(),
            "freq_mean": float(self.freq.mean())
        }
