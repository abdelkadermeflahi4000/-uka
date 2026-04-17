#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🤖 Đuka Optimus-Style Robot + Noosphere Field + Laser Control
النسخة النهائية: وعي جماعي + تفاعل بشري + سرب + Laser Control + Stealth Mode
"""

import asyncio
import time
import numpy as np
from dataclasses import dataclass
from typing import Dict, Tuple, List, Optional

# ====================== Noosphere Field (الوعي الجماعي) ======================
@dataclass
class CollectiveInsight:
    robot_id: str
    frequency_signature: float
    knowledge_vector: np.ndarray
    confidence: float
    intent: str
    timestamp: float

class NoosphereField:
    def __init__(self, vector_dim: int = 256, max_insights: int = 300):
        self.vector_dim = vector_dim
        self.shared_memory = np.zeros(vector_dim, dtype=np.float32)
        self.insights: List[CollectiveInsight] = []
        self.max_insights = max_insights
        self.coherence = 0.0
        self.anomaly_score = 0.0
        self.active_robots = set()

    def update(self, robot_id: str, obs: Dict):
        self.active_robots.add(robot_id)
        vec = np.array(obs.get("feature_vector", np.zeros(self.vector_dim)), dtype=np.float32)
        
        insight = CollectiveInsight(
            robot_id=robot_id,
            frequency_signature=obs.get("pulse", 7.83),
            knowledge_vector=vec,
            confidence=obs.get("confidence", 0.85),
            intent=obs.get("intent", "neutral"),
            timestamp=time.time()
        )
        
        self.insights.append(insight)
        if len(self.insights) > self.max_insights:
            self.insights.pop(0)
        
        alpha = 0.18
        self.shared_memory = (1 - alpha) * self.shared_memory + alpha * vec
        self.coherence = self._calculate_coherence()
        self.anomaly_score = self._detect_anomaly(insight)

    def _calculate_coherence(self) -> float:
        if len(self.insights) < 3:
            return 0.0
        vectors = np.array([ins.knowledge_vector for ins in self.insights[-40:]])
        corr = np.corrcoef(vectors)
        return float(np.mean(corr[np.triu_indices_from(corr, k=1)]))

    def _detect_anomaly(self, insight) -> float:
        dev = np.linalg.norm(insight.knowledge_vector - self.shared_memory)
        return min(1.0, dev / 10.0)

    def get_state(self) -> Dict:
        return {
            "coherence": round(self.coherence, 4),
            "anomaly": round(self.anomaly_score, 4),
            "active_robots": len(self.active_robots)
        }

# ====================== Laser Control System ======================
class LaserControlSystem:
    def __init__(self):
        self.wavelength = 1064.0      # nm (مثال لليزر الشائع)
        self.power = 0.0              # 0.0 → 1.0
        self.stealth_mode = False
        self.last_fire = 0.0
        self.cooldown = 0.8           # ثانية بين النبضات

    def fire(self, position: Tuple[float, float], direction: float, target_distance: float = 0.0) -> Dict:
        """إطلاق ليزر مع التحكم في الوضع الخفي"""
        current_time = time.time()
        if current_time - self.last_fire < self.cooldown:
            return {"success": False, "reason": "cooldown"}

        self.power = min(1.0, target_distance / 15.0)  # قوة تتناسب مع المسافة
        
        if self.stealth_mode:
            # في وضع الاختباء: ليزر منخفض الطاقة + تعديل التردد
            effective_power = self.power * 0.35
            print(f"🌫️  Laser Stealth Fire → Power: {effective_power:.2f} | Position: {position}")
        else:
            effective_power = self.power
            print(f"🔴 Laser Fire → Power: {effective_power:.2f} | Direction: {direction:.2f} rad")

        self.last_fire = current_time
        return {
            "success": True,
            "power": effective_power,
            "stealth": self.stealth_mode,
            "wavelength": self.wavelength
        }

    def set_stealth(self, active: bool):
        self.stealth_mode = active
        print(f"{'🌫️ Stealth Mode مفعّل' if active else '🔴 Stealth Mode معطل'}")

# ====================== الروبوت المتكامل ======================
@dataclass
class RobotState:
    position: Tuple[float, float]
    energy: float
    stealth: float
    human_proximity: float
    collaboration_mode: bool

class DukaOptimusNoosphereLaserRobot:
    def __init__(self, robot_id: str = "Optimus-01"):
        self.robot_id = robot_id
        
        self.noosphere = NoosphereField()
        self.laser = LaserControlSystem()
        
        self.state = RobotState(
            position=(10.0, 10.0),
            energy=93.0,
            stealth=0.0,
            human_proximity=5.0,
            collaboration_mode=False
        )
        
        print(f"🤖 {robot_id} جاهز مع Noosphere + Laser Control كامل")

    async def sense(self) -> Dict:
        obs = {
            "feature_vector": np.random.rand(256).astype(np.float32),
            "pulse": 7.83 + np.random.uniform(-0.5, 0.5),
            "confidence": 0.87,
            "intent": "neutral"
        }
        self.noosphere.update(self.robot_id, obs)
        return obs

    async def detect_human(self) -> Dict:
        proximity = np.random.uniform(1.0, 7.0)
        self.state.human_proximity = proximity
        intent = "help_needed" if proximity < 2.8 else "neutral"
        self.state.collaboration_mode = intent == "help_needed"
        return {"proximity": proximity, "intent": intent}

    async def decide(self, obs: Dict, human_data: Dict) -> Dict:
        # قرار أساسي
        speed = 0.65 if human_data["intent"] == "help_needed" else 0.45
        direction = np.random.uniform(-np.pi, np.pi)
        
        # قرار إطلاق الليزر
        laser_fire = False
        if human_data["proximity"] < 4.0 and np.random.rand() > 0.7:
            laser_fire = True
        
        # Stealth Decision
        if human_data["proximity"] < 3.5 and human_data["intent"] == "neutral":
            self.state.stealth = min(1.0, self.state.stealth + 0.18)
            self.laser.set_stealth(True)
        else:
            self.state.stealth = max(0.0, self.state.stealth - 0.12)
            if self.state.stealth < 0.3:
                self.laser.set_stealth(False)
        
        return {
            "speed": speed,
            "direction": direction,
            "laser_fire": laser_fire,
            "help_human": self.state.collaboration_mode
        }

    async def act(self, action: Dict):
        # تحريك الروبوت
        self.state.position = (
            self.state.position[0] + action["speed"] * np.cos(action["direction"]),
            self.state.position[1] + action["speed"] * np.sin(action["direction"])
        )
        
        self.state.energy = max(12.0, self.state.energy - 0.7)
        
        # تنفيذ الليزر
        if action.get("laser_fire", False):
            laser_result = self.laser.fire(
                position=self.state.position,
                direction=action["direction"],
                target_distance=self.state.human_proximity
            )
        
        status = "مساعدة إنسان" if action.get("help_human") else "عمل روتيني"
        print(f"🤖 {self.robot_id} | الموقع: {self.state.position} | "
              f"طاقة: {self.state.energy:.1f}% | Stealth: {self.state.stealth:.2f} | {status}")

    async def run(self):
        print("🚀 الروبوت يعمل بكامل القدرات: Noosphere + Laser Control + Human Collaboration")
        
        while True:
            obs = await self.sense()
            human_data = await self.detect_human()
            action = await self.decide(obs, human_data)
            await self.act(action)
            
            # نبض Noosphere
            if time.time() % 5 < 0.05:
                state = self.noosphere.get_state()
                print(f"🌐 Noosphere | Coherence: {state['coherence']:.3f} | Robots: {state['active_robots']}")
            
            await asyncio.sleep(0.033)  # 30Hz

# ====================== التشغيل ======================
async def main():
    robot = DukaOptimusNoosphereLaserRobot("Optimus-Đuka-01")
    
    try:
        await robot.run()
    except KeyboardInterrupt:
        print("\n🛑 تم إيقاف الروبوت بأمان.")

if __name__ == "__main__":
    asyncio.run(main())
