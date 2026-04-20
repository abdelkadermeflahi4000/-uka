class GlobalConsciousness:
    def __init__(self):
        self.awareness = 0.0

    def update(self, graph):
        self.awareness = graph.global_coherence()

    def state(self):
        return {
            "global_awareness": self.awareness
        }
