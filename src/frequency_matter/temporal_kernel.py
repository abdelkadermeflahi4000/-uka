"""⏳ TemporalKernel - زمن قابل للبرمجة داخل المحاكاة
يتيح التمدد، الضغط، والتخطي الزمني دون كسر السببية أو حد الـ 30Hz.
"""
import time
import torch
from typing import Literal
import logging

logger = logging.getLogger("duka.time")

class TemporalKernel:
    def __init__(self, base_hz: float = 30.0, dilation_bounds: tuple = (0.5, 2.0)):
        self.base_hz = base_hz
        self.min_d, self.max_d = dilation_bounds
        self.dilation = 1.0
        self.tick_accumulator = 0.0
        self.sim_time = 0.0
        self.real_start = time.perf_counter()
        
    def set_dilation(self, target: float, ramp_sec: float = 1.0):
        self.dilation = torch.clamp(torch.tensor(target), self.min_d, self.max_d).item()
        logger.info(f"⏳ Temporal dilation set to {self.dilation:.2f}x")
        
    def step(self, real_dt: float) -> float:
        sim_dt = real_dt * self.dilation
        self.sim_time += sim_dt
        self.tick_accumulator += sim_dt
        return sim_dt
        
    def should_tick(self) -> bool:
        threshold = 1.0 / self.base_hz
        if self.tick_accumulator >= threshold:
            self.tick_accumulator -= threshold
            return True
        return False
        
    def get_status(self) -> dict:
        return {
            "sim_time": self.sim_time,
            "dilation": self.dilation,
            "real_elapsed": time.perf_counter() - self.real_start,
            "sim_real_ratio": self.sim_time / max(1e-6, time.perf_counter() - self.real_start)
        }
