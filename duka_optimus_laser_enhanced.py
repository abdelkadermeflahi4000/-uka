#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🔴 Đuka Optimus Robot – Laser Control System v3.0 (متقدم)
يشمل: ترددات متعددة + أنماط إطلاق ذكية + تكيف مع Noosphere + Stealth/Combat Modes
"""

import asyncio
import time
import numpy as np
from dataclasses import dataclass
from enum import Enum
from typing import Dict, Tuple, List, Optional

# ====================== أنماط الليزر (Laser Patterns) ======================
class LaserPattern(Enum):
    SINGLE_PULSE = "single_pulse"      # نبضة واحدة
    BURST = "burst"                    # سلسلة نبضات سريعة
    CONTINUOUS = "continuous"          # مستمر (للقطع)
    STEALTH_SCAN = "stealth_scan"      # مسح خفي منخفض الطاقة
    PRECISION = "precision"            # دقة عالية + تردد محدد

# ====================== نظام الليزر المتقدم ======================
@dataclass
class LaserConfig:
    wavelength_nm: float      # الطول الموجي (nm)
    power_level: float        # 0.0 - 1.0
    pulse_duration_ms: float
    duty_cycle: float         # نسبة التشغيل
    pattern: LaserPattern
    stealth_factor: float     # تقليل التوقيع

class AdvancedLaserSystem:
    def __init__(self):
        self.configs = {
            "default": LaserConfig(1064.0, 0.6, 50.0, 0.4, LaserPattern.SINGLE_PULSE, 1.0),
            "stealth": LaserConfig(1550.0, 0.25, 20.0, 0.15, LaserPattern.STEALTH_SCAN, 0.35),
            "burst":   LaserConfig(532.0,  0.85, 8.0,  0.7,  LaserPattern.BURST, 0.9),
            "precision": LaserConfig(1064.0, 0.45, 120.0, 0.25, LaserPattern.PRECISION, 0.8)
        }
        self.current_config = self.configs["default"]
        self.last_fire_time = 0.0
        self.fire_history: List[Dict] = []   # سجل كل نبضة

    def set_mode(self, mode: str):
        """تغيير وضع الليزر"""
        if mode in self.configs:
            self.current_config = self.configs[mode]
            print(f"🔄 Laser Mode changed to: {mode.upper()} | Wavelength: {self.current_config.wavelength_nm}nm")
        else:
            print(f"⚠️  وضع غير معروف: {mode}")

    def fire(self, position: Tuple[float, float], direction: float, target_info: Dict = None) -> Dict:
        """إطلاق ليزر متقدم"""
        now = time.time()
        if now - self.last_fire_time < (self.current_config.pulse_duration_ms / 1000.0):
            return {"success": False, "reason": "cooldown_active"}

        target_distance = target_info.get("distance", 5.0) if target_info else 5.0
        power = self.current_config.power_level * (1.0 - target_distance / 30.0)
        power = max(0.1, min(1.0, power))

        # حساب التوقيع الترددي
        signature = self.current_config.wavelength_nm / 1000.0 * power

        result = {
            "success": True,
            "wavelength_nm": self.current_config.wavelength_nm,
            "power": round(power, 3),
            "pattern": self.current_config.pattern.value,
            "stealth_factor": self.current_config.stealth_factor,
            "signature": round(signature, 4),
            "position": position,
            "direction": round(direction, 3),
            "timestamp": now
        }

        self.fire_history.append(result)
        self.last_fire_time = now

        # طباعة حسب الوضع
        if self.current_config.pattern == LaserPattern.STEALTH_SCAN:
            print(f"🌫️  STEALTH LASER SCAN → Power: {power:.3f} | Sig: {signature:.3f}")
        elif self.current_config.pattern == LaserPattern.BURST:
            print(f"💥 BURST FIRE → Power: {power:.3f} | Wavelength: {self.current_config.wavelength_nm}nm")
        else:
            print(f"🔴 LASER FIRE → Power: {power:.3f} | Pattern: {self.current_config.pattern.value}")

        return result

    def get_statistics(self) -> Dict:
        """إحصائيات الليزر"""
        if not self.fire_history:
            return {"total_fires": 0}
        powers = [f["power"] for f in self.fire_history]
        return {
            "total_fires": len(self.fire_history),
            "avg_power": round(np.mean(powers), 3),
            "max_power": round(max(powers), 3),
            "stealth_fires": sum(1 for f in self.fire_history if f["stealth_factor"] < 0.6)
        }

# ====================== الروبوت المتكامل مع Laser ======================
@dataclass
class RobotState:
    position: Tuple[float, float]
    energy: float
    stealth: float
    human_proximity: float
    collaboration_mode: bool

class DukaOptimusLaserRobot:
    def __init__(self, robot_id: str = "Optimus-Laser-01"):
        self.robot_id = robot_id
        self.noosphere = NoosphereField()
        self.laser = AdvancedLaserSystem()
        
        self.state = RobotState(
            position=(10.0, 10.0),
            energy=92.0,
            stealth=0.0,
            human_proximity=6.0,
            collaboration_mode=False
        )
        
        print(f"🔴 {robot_id} جاهز مع Noosphere + Advanced Laser Control System")

    async def sense(self) -> Dict:
        obs = {
            "feature_vector": np.random.rand(256).astype(np.float32),
            "pulse": 7.83 + np.random.uniform(-0.6, 0.6),
            "confidence": 0.89,
            "intent": "neutral"
        }
        self.noosphere.update(self.robot_id, obs)
        return obs

    async def detect_human(self) -> Dict:
        proximity = np.random.uniform(1.5, 8.0)
        self.state.human_proximity = proximity
        intent = "help_needed" if proximity < 3.2 else "neutral"
        self.state.collaboration_mode = intent == "help_needed"
        return {"proximity": proximity, "intent": intent}

    async def decide(self, obs: Dict, human_data: Dict) -> Dict:
        speed = 0.7 if human_data["intent"] == "help_needed" else 0.45
        direction = np.random.uniform(-np.pi, np.pi)
        
        # قرار الليزر
        laser_fire = False
        laser_mode = "default"
        
        if human_data["proximity"] < 4.5:
            if np.random.rand() > 0.65:   # احتمال إطلاق
                laser_fire = True
                laser_mode = "precision" if human_data["intent"] == "help_needed" else "stealth"
        
        # تحديث Stealth
        if human_data["proximity"] < 3.8 and human_data["intent"] == "neutral":
            self.state.stealth = min(1.0, self.state.stealth + 0.22)
        else:
            self.state.stealth = max(0.0, self.state.stealth - 0.18)
        
        return {
            "speed": speed,
            "direction": direction,
            "laser_fire": laser_fire,
            "laser_mode": laser_mode,
            "help_human": self.state.collaboration_mode
        }

    async def act(self, action: Dict):
        # تحريك الروبوت
        self.state.position = (
            self.state.position[0] + action["speed"] * np.cos(action["direction"]),
            self.state.position[1] + action["speed"] * np.sin(action["direction"])
        )
        self.state.energy = max(10.0, self.state.energy - 0.75)

        # تنفيذ الليزر
        if action.get("laser_fire", False):
            target_info = {"distance": self.state.human_proximity}
            self.laser.set_mode(action["laser_mode"])
            result = self.laser.fire(
                position=self.state.position,
                direction=action["direction"],
                target_info=target_info
            )

        status = "مساعدة إنسان" if action.get("help_human") else "عمل روتيني"
        print(f"🤖 {self.robot_id} | الموقع: {self.state.position} | "
              f"طاقة: {self.state.energy:.1f}% | Stealth: {self.state.stealth:.2f} | {status}")

    async def run(self):
        print("🚀 الروبوت يعمل بـ Advanced Laser Control + Noosphere Field")
        
        while True:
            obs = await self.sense()
            human_data = await self.detect_human()
            action = await self.decide(obs, human_data)
            await self.act(action)
            
            # نبض Noosphere
            if int(time.time()) % 6 == 0:
                state = self.noosphere.get_state()
                laser_stats = self.laser.get_statistics()
                print(f"🌐 Noosphere | Coherence: {state['coherence']:.3f} | "
                      f"Laser Fires: {laser_stats['total_fires']}")
            
            await asyncio.sleep(0.033)  # 30Hz

# ====================== التشغيل ======================
async def main():
    robot = DukaOptimusLaserRobot("Optimus-Laser-01")
    
    try:
        await robot.run()
    except KeyboardInterrupt:
        print("\n🛑 تم إيقاف النظام بأمان.")
        laser_stats = robot.laser.get_statistics()
        print(f"📊 إحصائيات الليزر النهائية: {laser_stats}")

if __name__ == "__main__":
    asyncio.run(main())
