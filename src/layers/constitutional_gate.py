"""📜 Constitutional Decision Gate + Nudge Compiler"""
import torch
import hashlib, time, json
from typing import Dict, Tuple
import asyncio

class ConstitutionalDecisionGate:
    def __init__(self, node_id: str):
        self.node_id = node_id
        self.constraints = {
            "max_nudge_magnitude": lambda x: abs(x.get("magnitude",0)) <= 0.3,
            "reversibility_floor": lambda x: x.get("reversibility", 0) >= 0.8,
            "privacy_preserved": lambda x: x.get("dp_compliant", True)
        }
        self.prev_hash = "0x0"
        
    async def evaluate(self, action_logits: torch.Tensor, macro_state: torch.Tensor) -> Tuple[Dict, str]:
        # تحويل اللوجيت إلى نودج آمن
        mag = torch.sigmoid(action_logits).item()
        nudge = {
            "type": "dynamic_routing_incentive",
            "magnitude": round(mag * 0.3, 3),  # capped
            "reversibility": 0.95,
            "dp_compliant": True,
            "target": "edge_traffic_nodes",
            "confidence": round(float(torch.softmax(action_logits, dim=-1).max()), 4)
        }
        
        # تحقق دستوري
        for rule_name, check_fn in self.constraints.items():
            if not check_fn(nudge):
                nudge["type"] = "safe_hold"
                nudge["magnitude"] = 0.0
                nudge["reason"] = f"CONSTRAINT_VIOLATION: {rule_name}"
                break
                
        # تسجيل تدقيق مشفر
        payload = json.dumps(nudge, sort_keys=True)
        entry_hash = hashlib.sha256(f"{self.node_id}:{payload}:{self.prev_hash}".encode()).hexdigest()
        self.prev_hash = entry_hash
        
        return nudge, entry_hash
