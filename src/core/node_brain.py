import numpy as np


class NodeBrain:
    def __init__(self, node_id, n_osc=32):
        self.node_id = node_id
        self.n_osc = n_osc

        self.phase = np.random.rand(n_osc) * 2 * np.pi
        self.freq = np.random.normal(6.0, 0.5, n_osc)

    def step(self, dt=0.05):
        self.phase += dt * self.freq
        self.phase %= 2 * np.pi

    def coherence(self):
        return np.abs(np.mean(np.exp(1j * self.phase)))

    def state(self):
        return {
            "id": self.node_id,
            "phase": self.phase.copy(),
            "coherence": self.coherence()
        }
