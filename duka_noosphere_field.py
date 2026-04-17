# duka_noosphere_field.py  (جزء من Đuka)
import numpy as np
import asyncio
from dataclasses import dataclass
from typing import List, Dict

@dataclass
class CollectiveInsight:
    source_robot: str
    frequency_signature: float
    knowledge_vector: np.ndarray
    confidence: float
    timestamp: float

class NoosphereField:
    def __init__(self, max_robots: int = 50):
        self.insights: List[CollectiveInsight] = []
        self.shared_memory = np.zeros((128,))  # متجه معرفة جماعي
        self.coherence = 0.0

    def update(self, robot_id: str, observation: Dict):
        """إضافة معرفة جديدة من روبوت"""
        freq_sig = observation.get("pulse", 7.83)
        vec = np.array(observation.get("feature_vector", np.zeros(128)))
        
        insight = CollectiveInsight(
            source_robot=robot_id,
            frequency_signature=freq_sig,
            knowledge_vector=vec,
            confidence=observation.get("confidence", 0.8),
            timestamp=time.time()
        )
        
        self.insights.append(insight)
        # دمج المعرفة في الذاكرة الجماعية
        self.shared_memory = 0.7 * self.shared_memory + 0.3 * vec
        self.coherence = self._calculate_coherence()

    def _calculate_coherence(self) -> float:
        """حساب مستوى التوافق الجماعي"""
        if not self.insights:
            return 0.0
        vectors = np.array([ins.knowledge_vector for ins in self.insights[-20:]])
        return float(np.mean(np.corrcoef(vectors)))  # الارتباط المتوسط

    def get_collective_knowledge(self) -> Dict:
        return {
            "coherence": self.coherence,
            "shared_vector": self.shared_memory.tolist(),
            "active_robots": len(set(ins.source_robot for ins in self.insights)),
            "latest_insight": self.insights[-1].__dict__ if self.insights else None
        }

    async def share_with_bridge(self):
        """مشاركة الوعي مع Viola-Omega Bridge"""
        while True:
            status = self.get_collective_knowledge()
            print(f"🌐 Noosphere → Bridge | Coherence: {status['coherence']:.3f} | Robots: {status['active_robots']}")
            await asyncio.sleep(5)

# مثال استخدام
async def demo():
    noosphere = NoosphereField()
    # روبوت 1 يكتشف شيئاً
    noosphere.update("Robot-01", {"pulse": 7.95, "feature_vector": np.random.rand(128), "confidence": 0.92})
    # روبوت 2 يضيف معرفته
    noosphere.update("Robot-02", {"pulse": 7.80, "feature_vector": np.random.rand(128), "confidence": 0.85})
    
    print(noosphere.get_collective_knowledge())

if __name__ == "__main__":
    asyncio.run(demo())
