"""🌊 FrequencyGridWorld - بيئة ترددية ذات انتشار موجي هرمي
كل خلية تحمل (Amplitude, Phase). التردد ينتشر كموجة ويعدل الحالة المكانية.
"""
import gymnasium as gym
import torch
import numpy as np
from typing import Dict, Tuple, Optional
from gymnasium import spaces
import logging

logger = logging.getLogger("duka.freq_world")

class FrequencyGridWorld(gym.Env):
    metadata = {"render_modes": ["human"], "render_fps": 10}
    
    def __init__(self, grid_size: int = 12, freq_bands: int = 3, max_steps: int = 150, render_mode: str = None):
        super().__init__()
        self.grid_size = grid_size
        self.freq_bands = freq_bands
        self.max_steps = max_steps
        self.render_mode = render_mode
        self.current_step = 0
        
        # مساحة الملاحظة: [agent_pos, field_amplitude, field_phase]
        self.observation_space = spaces.Dict({
            "agent_pos": spaces.Box(low=0, high=grid_size-1, shape=(2,), dtype=np.int32),
            "field_amp": spaces.Box(low=0, high=1, shape=(freq_bands, grid_size, grid_size), dtype=np.float32),
            "field_phase": spaces.Box(low=-np.pi, high=np.pi, shape=(freq_bands, grid_size, grid_size), dtype=np.float32)
        })
        
        # أفعال: [move_4, emit_freq_band, morph_target]
        self.action_space = spaces.Dict({
            "move": spaces.Discrete(5),
            "emit_band": spaces.Discrete(freq_bands),
            "morph": spaces.Box(low=0, high=1, shape=(2,), dtype=np.float32)
        })
        
        self._reset_field()
        
    def _reset_field(self):
        self.field_amp = torch.rand(self.freq_bands, self.grid_size, self.grid_size) * 0.3
        self.field_phase = torch.rand(self.freq_bands, self.grid_size, self.grid_size) * 2 * np.pi - np.pi
        self.agent_pos = torch.tensor([self.grid_size//2, self.grid_size//2], dtype=torch.int32)
        self.current_step = 0
        
    def reset(self, seed=None, options=None):
        super().reset(seed=seed)
        self._reset_field()
        return self._get_obs(), {}
    
    def _propagate_wave(self, band: int, dt: float = 0.033):
        """انتشار موجي سريع (Laplacian approximation)"""
        pad = torch.nn.functional.pad(self.field_amp[band].unsqueeze(0), pad=(1,1,1,1), mode='reflect')
        lap = (pad[:, :-2, 1:-1] + pad[:, 2:, 1:-1] + pad[:, 1:-1, :-2] + pad[:, 1:-1, 2:] - 4*self.field_amp[band].unsqueeze(0))
        self.field_amp[band] = torch.clamp(self.field_amp[band] + 0.15 * lap.squeeze(0), 0, 1)
        self.field_phase[band] = torch.remainder(self.field_phase[band] + 2*np.pi*dt, 2*np.pi)
        
    def _get_obs(self):
        return {
            "agent_pos": self.agent_pos.numpy(),
            "field_amp": self.field_amp.numpy(),
            "field_phase": self.field_phase.numpy()
        }
    
    def step(self, action):
        self.current_step += 1
        
        # حركة الوكيل
        dx, dy = [(0,0), (-1,0), (1,0), (0,-1), (0,1)][int(action["move"])]
        self.agent_pos = torch.clamp(self.agent_pos + torch.tensor([dx, dy]), 0, self.grid_size-1)
        
        # بث ترددي + تحديث الحقل
        band = int(action["emit_band"])
        amp_boost = torch.zeros_like(self.field_amp)
        x, y = self.agent_pos
        amp_boost[band, x-1:x+2, y-1:y+2] += 0.25
        self.field_amp = torch.clamp(self.field_amp + amp_boost, 0, 1)
        self._propagate_wave(band)
        
        # مكافأة: ترابط ترددي + تقليل فوضى الطور
        local_amp = self.field_amp[:, x, y].mean().item()
        local_phase_var = self.field_phase[:, x, y].var().item()
        reward = local_amp * 2.0 - local_phase_var * 0.5
        
        terminated = self.current_step >= self.max_steps
        info = {"band_energy": local_amp, "phase_coherence": 1 - local_phase_var/np.pi**2}
        
        return self._get_obs(), reward, terminated, False, info
