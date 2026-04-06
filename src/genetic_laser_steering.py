"""🧬 Genetic Laser Steering - خريطة الجينوم → معاملات فيزيائية دقيقة
يتحكم مباشرة في: wavelength, polarization, phase, beam profile, pulse, stealth
"""
import numpy as np
from dataclasses import dataclass
from typing import Tuple, Dict, Optional
import logging

logger = logging.getLogger("duka.genetic_laser")

@dataclass
class PhysicalLaserConfig:
    """تكوين ليزر فيزيائي كامل قابل للتنفيذ في المحاكاة"""
    wavelength_nm: float          # 400-1500 nm (يحدد التفاعل مع المادة)
    polarization_angle: float     # 0-180° (زاوية الاستقطاب الخطي/البيضاوي)
    ellipticity: float            # -1.0 → +1.0 (خطي ↔ دائري)
    phase_offset: float           # -π → +π (إزاحة الطور الأولية)
    coherence_time: float         # 0.5-4.0 (خطوات محاكاة - وقت التماسك)
    beam_waist: float             # 0.5-2.5 خلية (عرض الحزمة عند المصدر)
    divergence: float             # 0.01-0.15 rad (تشتت الشعاع)
    pulse_duration: int           # 1-8 خطوات (مدة النبضة)
    duty_cycle: float             # 0.2-0.95 (نسبة التشغيل/الإيقاف)
    max_power: float              # 0.1-0.85 (الطاقة القصوى المسموحة)
    phase_lock_strength: float    # 0.0-1.0 (قوة مزامنة الطور مع الحقل)
    stealth_cutoff: float         # 0.6-0.99 (عتبة إخفاء الترددات العالية)

class GenomeLaserMapper:
    """يحوّل الجينوم (32 بعد) إلى تكوين ليزر فيزيائي مُقيّد دستورياً"""
    def __init__(self, constitutional_limits: Optional[Dict] = None):
        self.limits = constitutional_limits or self._default_limits()
        
    def _default_limits(self) -> Dict:
        return {
            "wavelength": (400.0, 1500.0),
            "polarization": (0.0, 180.0),
            "ellipticity": (-1.0, 1.0),
            "phase_offset": (-np.pi, np.pi),
            "coherence": (0.5, 4.0),
            "beam_waist": (0.5, 2.5),
            "divergence": (0.01, 0.15),
            "pulse_dur": (1, 8),
            "duty": (0.2, 0.95),
            "power": (0.1, 0.85),
            "phase_lock": (0.0, 1.0),
            "stealth": (0.6, 0.99)
        }

    def map(self, genome: np.ndarray) -> PhysicalLaserConfig:
        """تعيين سلس من الجينوم → معاملات فيزيائية"""
        def norm(v): return np.clip(v, -1.0, 1.0)
        def scale(v, mn, mx): return mn + (norm(v) + 1.0) / 2.0 * (mx - mn)
        
        return PhysicalLaserConfig(
            wavelength_nm=scale(genome[4], *self.limits["wavelength"]),
            polarization_angle=scale(genome[5], *self.limits["polarization"]),
            ellipticity=norm(genome[6]),
            phase_offset=norm(genome[7]) * np.pi,
            coherence_time=scale(genome[8], *self.limits["coherence"]),
            beam_waist=scale(genome[9], *self.limits["beam_waist"]),
            divergence=scale(genome[10], *self.limits["divergence"]),
            pulse_duration=int(max(1, scale(genome[11], *self.limits["pulse_dur"]))),
            duty_cycle=scale(genome[12], *self.limits["duty"]),
            max_power=scale(genome[13], *self.limits["power"]),
            phase_lock_strength=norm(genome[14]),
            stealth_cutoff=scale(genome[15], *self.limits["stealth"])
        )

    def validate_constitutional(self, cfg: PhysicalLaserConfig) -> Tuple[bool, str]:
        """فحص دستوري صارم قبل التنفيذ"""
        if cfg.wavelength_nm < 450 or cfg.wavelength_nm > 1400:
            return False, "WAVELENGTH_OUT_OF_SAFE_BAND"
        if cfg.max_power > 0.85:
            return False, "THERMAL_POWER_EXCEEDED"
        if cfg.duty_cycle > 0.92 and cfg.pulse_duration < 2:
            return False, "CONTINUOUS_BURN_RISK"
        if cfg.divergence > 0.12 and cfg.beam_waist < 0.8:
            return False, "UNCONTROLLED_SCATTERING"
        return True, "COMPLIANT"

    def apply_stealth_mask(self, obs_freq_field: np.ndarray, stealth_cutoff: float) -> np.ndarray:
        """يخفي الترددات فوق العتبة الجينية (محاكاة الإدراك المحدود)"""
        mask = np.ones_like(obs_freq_field)
        mask[obs_freq_field > stealth_cutoff] = 0.0
        return obs_freq_field * mask
