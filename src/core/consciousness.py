class ConsciousnessLayer:
    def __init__(self):
        self.attention = 0.0
        self.awareness = 0.0
        self.identity_score = 0.0

    def update(self, core_state, global_coherence):
        local = core_state["coherence"]

        self.attention = local
        self.awareness = (local + global_coherence) / 2.0
        self.identity_score = 0.8 * self.identity_score + 0.2 * local

    def get_state(self):
        return {
            "attention": self.attention,
            "awareness": self.awareness,
            "identity_score": self.identity_score
        }
