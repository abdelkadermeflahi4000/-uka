"""🔮 ProgrammableMatterSimulator - تحويل التردد إلى شكل/وظيفة
يحاكي "المادة القابلة للبرمجة" كحقل استجابة ترددي.
"""
import torch
import numpy as np
from typing import Dict, Tuple
import logging

logger = logging.getLogger("duka.matter")

class MorphologyField:
    def __init__(self, resolution: int = 16, device: str = "cpu"):
        self.res = resolution
        self.device = device
        # خريطة كثافة + توجيه (محاكاة جسم شبه مرن)
        self.density = torch.ones(resolution, resolution, device=device) * 0.5
        self.orientation = torch.zeros(resolution, resolution, device=device)
        
    def apply_frequency_response(self, freq_amp: torch.Tensor, freq_phase: torch.Tensor, morph_params: np.ndarray):
        """يعدل الكثافة والتوجيه استجابة للترددات المستلمة"""
        # تقليص/توسيع حسب السعة
        target_density = 0.2 + 0.6 * freq_amp.mean(0).to(self.device)
        self.density = torch.lerp(self.density, target_density, morph_params[0])
        
        # دوران/انحناء حسب الطور
        phase_map = freq_phase.mean(0).to(self.device)
        self.orientation = torch.lerp(self.orientation, phase_map, morph_params[1])
        
        return {"density_std": self.density.std().item(), "orientation_var": self.orientation.var().item()}
    
    def get_shape_state(self) -> Dict:
        return {
            "centroid": torch.stack(torch.where(self.density > 0.6)).mean(dim=1).tolist(),
            "spread": (self.density > 0.6).sum().item(),
            "anisotropy": float(torch.corrcoef(self.orientation.flatten(), self.density.flatten())[0,1])
        }
