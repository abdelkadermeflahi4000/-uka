#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🤖 Đuka Optimus-Style Robot Controller
روبوت أوبتيموس داخل Đuka – مع الترددات + الوعي الجماعي + الحماية الدستورية
"""

import time
import numpy as np
import asyncio
from dataclasses import dataclass
from typing import Dict, Tuple, Optional

# استيراد مكونات Đuka
from frequency_matter.frequency_grid_world import FrequencyGridWorld
from frequency_matter.genetic_agent import GeneticAgent
from frequency_matter.noosphere_layer import NoosphereField
from frequency_matter.morphology_field import MorphologyField

# Constitutional Guardrail (من Đuka)
from ĐukaCognitivePipeline import ConstitutionalGuardrail, NudgeIntervention

@dataclass
class RobotState:
    position: Tuple[float, float]
    velocity: Tuple[float, float]
    energy: float
    coherence: float
    last_pulse: float

class DukaOptimusRobot:
    def __init__(self, robot_id: str = "Optimus-01"):
        self.robot_id = robot_id
        self.world = FrequencyGridWorld(grid_size=16, freq_bands=4)
        self.agent = GeneticAgent(device="cpu")
        self.noosphere = NoosphereField(n_agents=20)
        self.morphology = MorphologyField(resolution=12)
        self.guardrail = ConstitutionalGuardrail()
        
        self.state = RobotState(
            position=(0.0, 0.0),
            velocity=(0.0, 0.0),
            energy=85.0,
            coherence=0.0,
            last_pulse=time.time()
        )
        
        print(f"🤖 روبوت {robot_id} تم تهيئته داخل Đuka Protocol")

    async def sense_environment(self) -> Dict:
        """استشعار البيئة عبر الترددات"""
        obs = self.world.get_observation()
        pulse = self.world.get_schumann_pulse()
        
        # تحديث الوعي الجماعي
        self.noosphere.update(obs["field_phase"], pollution_influx=0.05)
        
        return {
            "position": self.state.position,
            "frequency_field": obs["field_amp"].mean(),
            "pulse": pulse,
            "coherence": self.noosphere.get_coherence(),
            "anomaly": self.noosphere.get_anomaly_score()
        }

    async def decide_action(self, observation: Dict) -> Dict:
        """اتخاذ قرار باستخدام Genetic Agent + Guardrail"""
        # قرار أولي من الـ Agent
        raw_action = self.agent.act(observation)
        
        # تحويل إلى Nudge Intervention للفحص الدستوري
        nudge = NudgeIntervention(
            type="movement",
            magnitude=raw_action.get("speed", 0.5),
            target_group="self",
            expected_effect={"collision_risk": 0.1},
            reversibility_score=0.95
        )
        
        # فحص دستوري
        approved, reason = self.guardrail.evaluate(nudge)
        
        if not approved:
            print(f"⚠️  تم رفض الحركة: {reason}")
            # إجراء آمن بديل
            safe_action = {"speed": 0.3, "direction": 0.0, "reason": reason}
            return safe_action
        
        return raw_action

    async def act(self, action: Dict):
        """تنفيذ الحركة مع تكيف المورفولوجيا"""
        # تطبيق Morphology Field
        morph_feedback = self.morphology.apply_frequency_response(
            action.get("speed", 0.5),
            action.get("direction", 0.0)
        )
        
        # تحديث الحالة
        self.state.position = (
            self.state.position[0] + action.get("speed", 0.0) * np.cos(action.get("direction", 0.0)),
            self.state.position[1] + action.get("speed", 0.0) * np.sin(action.get("direction", 0.0))
        )
        
        self.state.energy = max(10.0, self.state.energy - 0.8)
        self.state.coherence = self.noosphere.get_coherence()
        
        print(f"🤖 {self.robot_id} تحرك → الموقع: {self.state.position} | الطاقة: {self.state.energy:.1f}% | التوافق: {self.state.coherence:.2f}")

    async def run_cycle(self):
        """دورة الروبوت الكاملة (Real-time)"""
        while True:
            obs = await self.sense_environment()
            action = await self.decide_action(obs)
            await self.act(action)
            
            # نبض مشترك مع الجسر (Viola-Omega)
            if time.time() - self.state.last_pulse > 4.0:
                print(f"🌍 نبض مشترك مع Viola-Omega Bridge: {FrequencyBus.get_pulse():.1f}%")
                self.state.last_pulse = time.time()
            
            await asyncio.sleep(0.033)  # 30Hz ≈ 33ms

    def get_status(self) -> Dict:
        return {
            "robot_id": self.robot_id,
            "position": self.state.position,
            "energy": self.state.energy,
            "coherence": self.state.coherence,
            "connected_to_noosphere": len(self.noosphere.agents) > 0
        }


# ====================== تشغيل الروبوت ======================
async def main():
    robot = DukaOptimusRobot("Optimus-Đuka-01")
    print("🚀 روبوت أوبتيموس داخل Đuka جاهز للعمل")
    
    try:
        await robot.run_cycle()
    except KeyboardInterrupt:
        print("\n🛑 تم إيقاف الروبوت بأمان.")
    except Exception as e:
        print(f"⚠️ خطأ: {e}")

if __name__ == "__main__":
    asyncio.run(main())
