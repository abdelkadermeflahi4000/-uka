from typing import List, Dict
from collections import deque


class CollectiveMemory:
    """الذاكرة الجماعية (Federated Knowledge Store)"""
    def __init__(self, max_entries: int = 500):
        self.patterns = deque(maxlen=max_entries)

    def store(self, node_state: Dict):
        self.patterns.append({
            "timestamp": __import__("time").time(),
            "node": node_state["id"],
            "coherence": node_state["coherence"],
            "phase_snapshot": node_state["phase"][:8]  # أول 8 لتوفير الذاكرة
        })

    def get_recent(self, n: int = 10) -> List[Dict]:
        return list(self.patterns)[-n:]

    def global_pattern_strength(self) -> float:
        if not self.patterns:
            return 0.0
        return float(np.mean([p["coherence"] for p in self.patterns]))
