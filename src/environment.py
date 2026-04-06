import gymnasium as gym
import numpy as np
from gymnasium import spaces
from typing import Dict, Optional, Tuple, List

class FrequencyGridWorld(gym.Env):
    """
    🌌 FrequencyGridWorld v2.0 - Đuka Protocol
    - حقل ترددي كامل
    - أشعة ليزر + أشعة صامتة (Silent Rays)
    - برمجة المادة + برمجة الزمن
    - Perfect Reality Match (لا أحد يشعر بالتدخل)
    """
    
    metadata = {"render_modes": ["human", "rgb_array"], "render_fps": 5}
    
    def __init__(
        self,
        grid_size: int = 12,
        max_steps: int = 150,
        n_resonators: int = 6,
        n_dissonance: int = 6,
        render_mode: Optional[str] = None,
    ):
        super().__init__()
        self.grid_size = grid_size
        self.max_steps = max_steps
        self.render_mode = render_mode
        
        self.action_space = spaces.Discrete(5)  # 0-3: حركة, 4: بقاء + إطلاق ليزر
        
        # الملاحظة: تردد + طور + سعة + time_field
        self.observation_space = spaces.Box(
            low=-1.0, high=1.0,
            shape=(grid_size, grid_size, 4),   # freq, phase, amp, time_flow
            dtype=np.float32
        )
        
        self.laser_beams: List[Dict] = []
        self._reset_environment()
    
    def _reset_environment(self):
        self.agent_pos = np.array([np.random.randint(0, self.grid_size), 
                                 np.random.randint(0, self.grid_size)])
        
        # الحقول الأساسية
        self.frequency_field = np.random.uniform(-0.6, 0.6, (self.grid_size, self.grid_size))
        self.phase_field = np.random.uniform(-np.pi, np.pi, (self.grid_size, self.grid_size))
        self.amplitude_field = np.random.uniform(0.4, 0.9, (self.grid_size, self.grid_size))
        self.time_field = np.ones((self.grid_size, self.grid_size))  # 1.0 = زمن طبيعي
        
        # Resonators (معرفة عالية)
        self.resonators = self._generate_positions(6)
        for pos in self.resonators:
            self.frequency_field[pos[0], pos[1]] = 0.92
            self.amplitude_field[pos[0], pos[1]] = 1.0
        
        # Dissonance (تلوث / أمراض)
        self.dissonance = self._generate_positions(6)
        for pos in self.dissonance:
            self.frequency_field[pos[0], pos[1]] = -0.85
            self.amplitude_field[pos[0], pos[1]] = 0.55
        
        self.laser_beams.clear()
        self.current_step = 0
        self.knowledge_collected = 0
        self.reality_match = 1.0  # Perfect Reality Match (0→1)
    
    def _generate_positions(self, n: int):
        positions = []
        while len(positions) < n:
            pos = np.array([np.random.randint(0, self.grid_size), 
                          np.random.randint(0, self.grid_size)])
            if not any(np.array_equal(pos, p) for p in positions):
                positions.append(pos)
        return np.array(positions)
    
    def add_laser_beam(self, start: tuple, direction: tuple, frequency: float, 
                      amplitude: float = 1.0, is_silent: bool = True, duration: int = 8):
        """إطلاق شعاع ليزر / أشعة صامتة"""
        self.laser_beams.append({
            "start": np.array(start, dtype=float),
            "dir": np.array(direction, dtype=float) / (np.linalg.norm(direction) + 1e-8),
            "freq": frequency,
            "amp": amplitude,
            "silent": is_silent,
            "remaining": duration
        })
    
    def reset(self, seed=None, options=None):
        super().reset(seed=seed)
        self._reset_environment()
        return self._get_observation(), {"reality_match": self.reality_match}
    
    def _get_observation(self):
        obs = np.zeros((self.grid_size, self.grid_size, 4), dtype=np.float32)
        obs[:, :, 0] = self.frequency_field
        obs[:, :, 1] = np.sin(self.phase_field)
        obs[:, :, 2] = self.amplitude_field
        obs[:, :, 3] = self.time_field
        return obs
    
    def step(self, action: int):
        # حركة الوكيل
        directions = [(-1,0), (1,0), (0,-1), (0,1), (0,0)]
        delta = directions[action]
        new_pos = self.agent_pos + delta
        if 0 <= new_pos[0] < self.grid_size and 0 <= new_pos[1] < self.grid_size:
            self.agent_pos = new_pos
        
        self.current_step += 1
        
        # تأثير الأشعة الليزر الحالية
        reward = 0.0
        for beam in self.laser_beams[:]:
            t = 0.0
            while t < self.grid_size * 1.5:
                pos = (beam["start"] + t * beam["dir"]).astype(int)
                if not (0 <= pos[0] < self.grid_size and 0 <= pos[1] < self.grid_size):
                    break
                
                dist = np.linalg.norm(pos - self.agent_pos) + 1e-6
                influence = beam["amp"] * np.exp(-dist * 0.8)
                
                # برمجة المادة
                self.frequency_field[pos[0], pos[1]] = beam["freq"] * influence * 0.7 + \
                                                      self.frequency_field[pos[0], pos[1]] * 0.3
                
                # برمجة الزمن
                self.time_field[pos[0], pos[1]] *= (1.0 + 0.12 * (beam["freq"] - 0.5))
                
                # Reality Match (كلما زاد الـ resonance كلما أصبح الواقع طبيعي)
                if beam["silent"] and abs(beam["freq"]) > 0.85:
                    self.reality_match = min(1.0, self.reality_match + 0.015)
                    reward += 0.8
                
                t += 0.6
            beam["remaining"] -= 1
            if beam["remaining"] <= 0:
                self.laser_beams.remove(beam)
        
        # Resonance & Dissonance
        freq = self.frequency_field[self.agent_pos[0], self.agent_pos[1]]
        amp = self.amplitude_field[self.agent_pos[0], self.agent_pos[1]]
        reward += freq * amp * 3.0
        
        # جمع Resonators
        for i, res in enumerate(self.resonators):
            if np.array_equal(self.agent_pos, res):
                reward += 8.0
                self.knowledge_collected += 1
                self.frequency_field[res[0], res[1]] += 0.15
        
        terminated = self.knowledge_collected >= 6 or self.reality_match >= 0.98
        truncated = self.current_step >= self.max_steps
        
        info = {
            "knowledge": self.knowledge_collected,
            "reality_match": round(self.reality_match, 3),
            "current_time_flow": float(self.time_field[self.agent_pos[0], self.agent_pos[1]]),
            "lasers_active": len(self.laser_beams)
        }
        
        return self._get_observation(), reward, terminated, truncated, info
    
    def render(self):
        # سيكون ملون حسب التردد + أشعة ليزر مرئية
        print(f"Pos: {self.agent_pos} | Reality Match: {self.reality_match:.3f} | Lasers: {len(self.laser_beams)}")
