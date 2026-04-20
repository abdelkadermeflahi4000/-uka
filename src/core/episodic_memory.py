import time


class EpisodicMemory:
    def __init__(self):
        self.episodes = []

    def store_episode(self, core_state, context=None):
        episode = {
            "timestamp": time.time(),
            "phase": core_state["phase"],
            "coherence": core_state["coherence"],
            "context": context
        }
        self.episodes.append(episode)

    def recall_closest(self, target_phase):
        if not self.episodes:
            return None

        best = None
        best_score = float("inf")

        for ep in self.episodes:
            diff = ((ep["phase"] - target_phase) ** 2).mean()

            if diff < best_score:
                best_score = diff
                best = ep

        return best

    def replay(self):
        for ep in self.episodes:
            yield ep
