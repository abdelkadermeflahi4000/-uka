"""⚡ Real-Time Deadline Enforcer & Fallback"""
import time
from typing import Dict, Optional

class DeadlineEnforcer:
    def __init__(self, budget_ms: float, fallback_ms: float):
        self.budget_ms = budget_ms
        self.fallback_ms = fallback_ms
        self.t_start = 0.0
        self.checkpoints: Dict[str, float] = {}
        
    def reset(self):
        self.t_start = time.perf_counter()
        self.checkpoints.clear()
        
    def checkpoint(self, name: str):
        elapsed = (time.perf_counter() - self.t_start) * 1000
        self.checkpoints[name] = elapsed
        
    def get_checkpoint(self, name: str) -> float:
        return self.checkpoints.get(name, 0.0)
        
    def is_over_budget(self) -> bool:
        return (time.perf_counter() - self.t_start) * 1000 > self.budget_ms

class FallbackPolicy:
    def __init__(self):
        self.active = False
        self.safe_action = {"type": "hold", "magnitude": 0.0}
        
    def activate(self):
        self.active = True
        # في الإنتاج: إطلاق إنذار، تبديل إلى سياسة محفوظة، عزل الشبكة
        
    def get_action(self):
        return self.safe_action
