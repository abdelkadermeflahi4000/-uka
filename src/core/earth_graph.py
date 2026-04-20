import numpy as np


class EarthGraph:
    def __init__(self):
        self.nodes = {}

    def update_node(self, node_id, state, location=None):
        self.nodes[node_id] = {
            "state": state,
            "location": location
        }

    def global_coherence(self):
        if not self.nodes:
            return 0.0

        phases = []

        for node in self.nodes.values():
            phase = node["state"]["phase"]
            phases.extend(phase[:5])  # sample partial phase

        phases = np.array(phases)

        return np.abs(np.mean(np.exp(1j * phases)))

    def neighbors(self, node_id):
        return [n for n in self.nodes if n != node_id]

    def get_network_state(self):
        return {
            "num_nodes": len(self.nodes),
            "global_coherence": self.global_coherence()
        }
