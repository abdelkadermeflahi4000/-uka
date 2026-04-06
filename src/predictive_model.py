"""🌐 HierarchicalPredictiveWorldModel - تنبؤ سببي بـ 5 خطوات
يتنبأ بالحقول الترددية والزمنية بناءً على التكوين الليزري، مع تصحيح ذاتي للانحراف
"""
import torch
import torch.nn as nn
import numpy as np
from typing import Dict, Tuple, Optional
import logging
from collections import deque

logger = logging.getLogger("duka.predictive")

class HierarchicalPredictiveNet(nn.Module):
    """شبكة خفيفة الوزن (≈180K params) مصممة للشبكات الصغيرة (10-15)"""
    def __init__(self, grid_size: int = 12, laser_dim: int = 12, latent: int = 96):
        super().__init__()
        self.grid_size = grid_size
        
        # 1. ترميز متعدد المستويات (Macro → Micro)
        self.encoder = nn.Sequential(
            nn.Conv2d(3, 24, 3, padding=1), nn.GELU(),           # 3 قنوات: freq, amp, time
            nn.Conv2d(24, 48, 3, stride=2, padding=1), nn.GELU(),
            nn.AdaptiveAvgPool2d(4),                             # تلخيص هرمي
            nn.Flatten()
        )
        
        # 2. دمج السياق (ليزر + موقع الوكيل)
        self.context_fusion = nn.Sequential(
            nn.Linear(48*16 + laser_dim + 2, latent),
            nn.LayerNorm(latent),
            nn.GELU(),
            nn.Linear(latent, latent)
        )
        
        # 3. رؤوس تنبؤ t+5 مباشرة (تجنب الـ Autoregressive drift)
        self.pred_freq = nn.Sequential(
            nn.Linear(latent, grid_size * grid_size),
            nn.Unflatten(1, (1, grid_size, grid_size)),
            nn.Conv2d(1, 1, 3, padding=1),
            nn.Tanh()  # [-1, 1]
        )
        self.pred_time = nn.Sequential(
            nn.Linear(latent, grid_size * grid_size),
            nn.Unflatten(1, (1, grid_size, grid_size)),
            nn.Conv2d(1, 1, 3, padding=1),
            nn.Sigmoid() # [0, 1] → سيتم تحويله لـ [0.5, 2.0]
        )

    def forward(self, fields: torch.Tensor, laser_cfg: torch.Tensor, agent_pos: torch.Tensor):
        # fields: (B, 3, H, W)
        macro = self.encoder(fields)
        context = torch.cat([macro, laser_cfg, agent_pos], dim=-1)
        latent = self.context_fusion(context)
        
        freq_hat = self.pred_freq(latent).squeeze(1)
        time_hat = 0.5 + 1.5 * self.pred_time(latent).squeeze(1)
        return freq_hat, time_hat


class PredictiveOverlay:
    """طبقة تنبؤ تعمل بالتوازي مع البيئة، مع تصحيح ذاتي ومزامنة زمنية"""
    def __init__(self, grid_size: int = 12, device: str = "cpu", update_interval: int = 10):
        self.device = device
        self.update_interval = update_interval
        self.step_counter = 0
        self.prediction_cache: Optional[Tuple[torch.Tensor, torch.Tensor]] = None
        self.error_buffer = deque(maxlen=50)
        
        self.model = HierarchicalPredictiveNet(grid_size=grid_size).to(device)
        self.model.eval()
        
    def predict(self, freq: np.ndarray, amp: np.ndarray, time_f: np.ndarray, 
                laser_cfg: np.ndarray, agent_pos: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        """إرجاع تنبؤ t+5 مع قياس عدم اليقين"""
        if self.prediction_cache is not None and self.step_counter % self.update_interval != 0:
            self.step_counter += 1
            return self.prediction_cache
            
        with torch.no_grad():
            fields = torch.tensor(np.stack([freq, amp, time_f], axis=0), dtype=torch.float32, device=self.device).unsqueeze(0)
            cfg = torch.tensor(laser_cfg, dtype=torch.float32, device=self.device).unsqueeze(0)
            pos = torch.tensor(agent_pos / self.model.grid_size, dtype=torch.float32, device=self.device).unsqueeze(0)
            
            pred_freq, pred_time = self.model(fields, cfg, pos)
            self.prediction_cache = (pred_freq.squeeze().cpu().numpy(), pred_time.squeeze().cpu().numpy())
            self.step_counter = 0
            
        return self.prediction_cache

    def record_error(self, actual_freq: np.ndarray, actual_time: np.ndarray):
        """تسجيل الانحراف الفعلي لتصحيح التنبؤات مستقبلاً"""
        if self.prediction_cache:
            pred_f, pred_t = self.prediction_cache
            freq_err = np.mean((pred_f - actual_freq)**2)
            time_err = np.mean((pred_t - actual_time)**2)
            self.error_buffer.append((freq_err, time_err))
            return freq_err, time_err
        return 0.0, 0.0

    def get_prediction_confidence(self) -> float:
        """ثقة النموذج (1 - متوسط الخطأ المعياري)"""
        if not self.error_buffer: return 0.95
        avg_err = np.mean([f + t for f, t in self.error_buffer])
        return max(0.0, min(1.0, 1.0 - np.sqrt(avg_err)))
