"""🔦 AutonomousLaserAgent - وكيل ليزر مستقل مع تحكم دستوري وجيني
يتعلم برمجة الحقول الترددية والزمنية عبر أشعة موجهة صامتة/علنية
"""
import numpy as np
import torch
from gymnasium import spaces
from gymnasium import Wrapper
from stable_baselines3 import PPO
from stable_baselines3.common.vec_env import DummyVecEnv
from typing import Dict, Tuple, Optional
import logging

logger = logging.getLogger("duka.laser_agent")

# ─────────────────────────────────────────────────────────────
# 🧭 طبقة التحويل الدستورية (Constitutional Laser Gate)
# ─────────────────────────────────────────────────────────────

class LaserConstitutionalGate:
    """فرض حدود فيزيائية وأمنية صارمة على توليد الليزر"""
    def __init__(
        self,
        max_amplitude: float = 0.9,
        freq_bounds: Tuple[float, float] = (-0.85, 0.85),
        max_simultaneous_beams: int = 6,
        min_cooldown_steps: int = 3
    ):
        self.max_amp = max_amplitude
        self.freq_bounds = freq_bounds
        self.max_beams = max_simultaneous_beams
        self.min_cooldown = min_cooldown_steps
        self.cooldown_counter = 0

    def validate_and_decay(self, beam_cmd: Dict) -> Tuple[bool, Dict, str]:
        if self.cooldown_counter > 0:
            self.cooldown_counter -= 1
            return False, beam_cmd, "COOLDOWN_ACTIVE"
            
        if beam_cmd.get("amplitude", 0) > self.max_amp:
            beam_cmd["amplitude"] = self.max_amp
        beam_cmd["frequency"] = np.clip(beam_cmd["frequency"], *self.freq_bounds)
        beam_cmd["amplitude"] = max(0.0, beam_cmd.get("amplitude", 0.0))
        
        return True, beam_cmd, "COMPLIANT"

    def trigger_cooldown(self, genome_vector: np.ndarray):
        # الجين 3 يتحكم في سرعة التبريد (0=بطيء, 1=سريع)
        efficiency = (genome_vector[3] + 1.0) / 2.0
        self.cooldown_counter = max(1, int(self.min_cooldown * (1.0 - 0.5 * efficiency)))

# ─────────────────────────────────────────────────────────────
# 🎮 Wrapper لتحويل البيئة إلى Continuous Laser Control
# ─────────────────────────────────────────────────────────────

class LaserControlWrapper(Wrapper):
    """يحول LaserFrequencyGridWorld إلى مساحة أفعال مستمرة مناسبة لـ PPO"""
    def __init__(self, env):
        super().__init__(env)
        # [dx, dy, aim_angle, freq, amp, trigger]
        self.action_space = spaces.Box(low=-1.0, high=1.0, shape=(6,), dtype=np.float32)
        self.gate = LaserConstitutionalGate()
        self.violation_count = 0

    def step(self, action: np.ndarray) -> Tuple[np.ndarray, float, bool, bool, Dict]:
        # 1. فك الشفرة الدستورية
        dx = int(np.round(action[0]))
        dy = int(np.round(action[1]))
        laser_cmd = {
            "angle": float(action[2] * np.pi),
            "frequency": float(action[3]),
            "amplitude": float(action[4]),
            "trigger": bool(action[5] > 0.0)
        }
        
        # 2. تحقق دستوري
        compliant, safe_cmd, reason = self.gate.validate_and_decay(laser_cmd)
        if not compliant:
            laser_cmd["trigger"] = False

        # 3. تنفيذ حركة الوكيل
        move_action = np.clip([dx + 2, dy + 2], 0, 4).tolist().index(2) if dx == 0 and dy == 0 else None
        base_action = 0  # stay
        if dx > 0: base_action = 3
        elif dx < 0: base_action = 2
        elif dy > 0: base_action = 4
        elif dy < 0: base_action = 1

        obs, reward, terminated, truncated, info = self.env.step(base_action)

        # 4. إطلاق الشعاع
        if laser_cmd["trigger"] and compliant:
            x, y = self.env.unwrapped.agent_pos
            direction = (np.cos(laser_cmd["angle"]), np.sin(laser_cmd["angle"]))
            self.env.unwrapped.add_laser_beam(
                (x, y), direction, safe_cmd["frequency"], safe_cmd["amplitude"], is_silent=True
            )
            self.gate.trigger_cooldown(self.genome_vector)
            
            # مكافأة الدقة الترددية
            actual_freq = self.env.unwrapped.freq_field[x, y]
            precision = 1.0 - min(1.0, abs(actual_freq - safe_cmd["frequency"]) * 1.5)
            reward += precision * 3.0
            reward -= safe_cmd["amplitude"] * 0.2  # تكلفة طاقة
            info["laser_precision"] = precision
        elif laser_cmd["trigger"] and not compliant:
            self.violation_count += 1
            reward -= 1.5
            info["constitutional_violation"] = reason

        return obs, float(reward), terminated, truncated, info

    def reset(self, **kwargs):
        self.violation_count = 0
        return self.env.reset(**kwargs)

# ─────────────────────────────────────────────────────────────
# 🧬 AutonomousLaserAgent
# ─────────────────────────────────────────────────────────────

class AutonomousLaserAgent:
    def __init__(self, env, config: dict, genome, node_id: str = "laser_01"):
        self.node_id = node_id
        self.genome = genome
        self.env = env
        self.env.unwrapped.genome_vector = genome.vector  # حقن للجينوم في البيئة
        
        self.model = PPO(
            policy="MlpPolicy",
            env=env,
            learning_rate=3e-4 * ((genome.vector[0] + 1.0) / 2.0),  # جين 0: معدل التعلم
            clip_range=0.2,
            n_steps=2048,
            batch_size=64,
            n_epochs=10,
            verbose=1,
            tensorboard_log=config["training"]["log_dir"]
        )
        
    def train(self, total_timesteps: int):
        logger.info(f"🔦 [{self.node_id}] Starting Laser Policy Training | Genome Fitness: {self.genome.fitness:.2f}")
        self.model.learn(total_timesteps=total_timesteps, progress_bar=True)
        
    def save(self, path: str):
        self.model.save(f"{path}_laser")
        np.save(f"{path}_laser_genome.npy", self.genome.vector)
        
    def load(self, path: str):
        self.model = PPO.load(f"{path}_laser", env=self.env)
        if __import__("os").path.exists(f"{path}_laser_genome.npy"):
            self.genome.vector = np.load(f"{path}_laser_genome.npy")
