class CollectiveMemory:
    def __init__(self):
        self.shared_patterns = []

    def store(self, node_state):
        self.shared_patterns.append({
            "node": node_state["id"],
            "phase": node_state["phase"],
            "coherence": node_state["coherence"]
        })

    def get_recent(self, n=5):
        return self.shared_patterns[-n:]
