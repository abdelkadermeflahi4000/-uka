#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🌐 Noosphere Field v2.1 – الوعي الجماعي في Đuka
"""

import numpy as np
import asyncio
import time
import json
from dataclasses import dataclass
from typing import Dict, List, Optional
from pathlib import Path

@dataclass
class CollectiveInsight:
    robot_id: str
    frequency_signature: float          # نبض التردد
    knowledge_vector: np.ndarray        # متجه المعرفة (256 بُعد)
    confidence: float
    intent: str                         # "help", "warning", "discovery", "neutral"
    timestamp: float

class NoosphereField:
    def __init__(self, max_insights: int = 200, vector_dim: int = 256):
        self.vector_dim = vector_dim
        self.shared_memory = np.zeros(vector_dim, dtype=np.float32)   # الذاكرة الجماعية
        self.insights: List[CollectiveInsight] = []
        self.max_insights = max_insights
        self.coherence = 0.0
        self.anomaly_score = 0.0
        self.active_robots = set()
        
        # ملف حفظ الذاكرة
        self.memory_file = Path(".noosphere_memory.json")
        self._load_persistent_memory()

    def _load_persistent_memory(self):
        if self.memory_file.exists():
            try:
                data = json.loads(self.memory_file.read_text(encoding="utf-8"))
                self.shared_memory = np.array(data.get("shared_memory", np.zeros(self.vector_dim)))
                print(f"🧠 تم تحميل ذاكرة Noosphere من الجيل السابق")
            except:
                pass

    def _save_persistent_memory(self):
        data = {
            "shared_memory": self.shared_memory.tolist(),
            "last_update": time.time(),
            "active_robots": len(self.active_robots)
        }
        self.memory_file.write_text(json.dumps(data, indent=2), encoding="utf-8")

    def update(self, robot_id: str, observation: Dict):
        """إضافة معرفة جديدة من روبوت"""
        self.active_robots.add(robot_id)
        
        vec = np.array(observation.get("feature_vector", np.zeros(self.vector_dim)), dtype=np.float32)
        pulse = observation.get("pulse", 7.83)
        confidence = observation.get("confidence", 0.85)
        intent = observation.get("intent", "neutral")
        
        insight = CollectiveInsight(
            robot_id=robot_id,
            frequency_signature=pulse,
            knowledge_vector=vec,
            confidence=confidence,
            intent=intent,
            timestamp=time.time()
        )
        
        self.insights.append(insight)
        if len(self.insights) > self.max_insights:
            self.insights.pop(0)
        
        # دمج المعرفة في الذاكرة الجماعية (Exponential Moving Average)
        alpha = 0.15
        self.shared_memory = (1 - alpha) * self.shared_memory + alpha * vec
        
        # تحديث التوافق والشذوذ
        self.coherence = self._calculate_coherence()
        self.anomaly_score = self._detect_anomaly(insight)
        
        # حفظ دوري
        if len(self.insights) % 20 == 0:
            self._save_persistent_memory()

    def _calculate_coherence(self) -> float:
        """حساب مستوى التوافق الجماعي"""
        if len(self.insights) < 2:
            return 0.0
        recent_vectors = np.array([ins.knowledge_vector for ins in self.insights[-30:]])
        corr_matrix = np.corrcoef(recent_vectors)
        return float(np.mean(corr_matrix[np.triu_indices_from(corr_matrix, k=1)]))

    def _detect_anomaly(self, insight: CollectiveInsight) -> float:
        """كشف السلوك الشاذ"""
        deviation = np.linalg.norm(insight.knowledge_vector - self.shared_memory)
        return float(min(1.0, deviation / 8.0))   # تطبيع

    def get_collective_state(self) -> Dict:
        """الحالة الجماعية الكاملة"""
        return {
            "coherence": round(self.coherence, 4),
            "anomaly_score": round(self.anomaly_score, 4),
            "active_robots": len(self.active_robots),
            "total_insights": len(self.insights),
            "shared_memory_norm": float(np.linalg.norm(self.shared_memory)),
            "latest_intent": self.insights[-1].intent if self.insights else "none"
        }

    def query(self, query_vector: np.ndarray, top_k: int = 5) -> List[CollectiveInsight]:
        """البحث الدلالي داخل الذاكرة الجماعية"""
        if not self.insights:
            return []
        
        scores = []
        for ins in self.insights[-100:]:   # آخر 100 insight فقط
            similarity = np.dot(ins.knowledge_vector, query_vector) / (
                np.linalg.norm(ins.knowledge_vector) * np.linalg.norm(query_vector) + 1e-8
            )
            scores.append((similarity, ins))
        
        scores.sort(reverse=True, key=lambda x: x[0])
        return [item[1] for item in scores[:top_k]]

    async def share_with_bridge(self):
        """مشاركة الحالة مع Viola-Omega Bridge"""
        while True:
            state = self.get_collective_state()
            print(f"🌐 Noosphere → Bridge | Coherence: {state['coherence']:.3f} | "
                  f"Robots: {state['active_robots']} | Anomaly: {state['anomaly_score']:.3f}")
            await asyncio.sleep(6)

# ====================== مثال تشغيل ======================
async def demo():
    noosphere = NoosphereField()
    
    # روبوت 1 يكتشف إنساناً يحتاج مساعدة
    noosphere.update("Robot-01", {
        "feature_vector": np.random.rand(256),
        "pulse": 8.1,
        "confidence": 0.93,
        "intent": "urgent_help"
    })
    
    # روبوت 2 يكتشف عقبة
    noosphere.update("Robot-02", {
        "feature_vector": np.random.rand(256),
        "pulse": 7.6,
        "confidence": 0.88,
        "intent": "obstacle"
    })
    
    print(noosphere.get_collective_state())
    
    # بحث دلالي
    query = np.random.rand(256)
    results = noosphere.query(query, top_k=3)
    print(f"نتائج البحث: {len(results)} insight")

if __name__ == "__main__":
    asyncio.run(demo())
