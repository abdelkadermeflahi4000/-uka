import asyncio
import numpy as np
import torch
from typing import List, Dict, Optional
from src.ogcg.global_consciousness import GlobalConsciousness
from src.hierarchical_world_model import HierarchicalWorldModel
from src.neural_surrogate import SurrogateSimulator
from src.reality_simulator import RealityReSimulator
from src.layers.constitutional_gate import ConstitutionalDecisionGate
from DP_FedAvg import DifferentialPrivacyWrapper
from src.noosphere import Noosphere as BaseNoosphere  # النسخة القديمة للتوافق

class ExpandedNoosphere(BaseNoosphere):
    """
    🌐 Noosphere v2 — الوعي الجماعي المتقدم في Đuka
    يدمج OGCG + Hierarchical + Surrogate + Reality Re-simulation
    """
    def __init__(self, num_agents: int = 12, grid_size: int = 20, 
                 enable_ogcg: bool = True, enable_reality_resim: bool = True):
        super().__init__(num_agents=num_agents, grid_size=grid_size)
        
        # ── OGCG Core (Global Consciousness)
        self.ogcg = GlobalConsciousness()
        for i in range(num_agents):
            self.ogcg.add_node(f"node_{i:03d}")
        
        # ── Hierarchical + Surrogate
        self.hierarchical_model = HierarchicalWorldModel(grid_size=grid_size)
        self.surrogate = SurrogateSimulator()
        
        # ── Reality Re-simulation
        self.reality_engine = RealityReSimulator(self) if enable_reality_resim else None
        
        # ── Privacy + Guardrail
        self.dp_wrapper = DifferentialPrivacyWrapper(noise_scale=0.08)
        self.constitutional_gate = ConstitutionalDecisionGate(node_id="noosphere_core")
        
        # ── Viral Propagation (انتشار الأفكار)
        self.viral_buffer = []  # قائمة النودج المنتشرة
        
        print(f"🌍 Expanded Noosphere v2 جاهز | Agents: {num_agents} | OGCG Enabled: {enable_ogcg}")

    async def run_expanded_cycle(self, sensor_frame: Optional[Dict] = None):
        """دورة Noosphere متقدمة (تُستدعى من realtime_pipeline)"""
        # 1. تحديث OGCG (30Hz)
        await self.ogcg.run_30hz(duration_steps=1)
        global_awareness = self.ogcg.awareness
        
        # 2. Hierarchical Compression
        agent_states = np.array([a.genome for a in self.agents])
        macros = self.hierarchical_model.compress_agents(agent_states, 
                                                         [a.get_behavior_dict() for a in self.agents])
        
        # 3. Surrogate Prediction
        macro_state = macros[0].centroid if macros else agent_states.mean(axis=0)
        pred = self.surrogate.predict_step(macro_state, np.zeros(4))
        
        # 4. Reality Re-simulation (إعادة بناء الواقع)
        if self.reality_engine:
            reality_layer = self.reality_engine.re_simulate(steps=10)
        
        # 5. Viral Thought Propagation
        await self._propagate_viral_thought(global_awareness)
        
        # 6. Constitutional + DP-Fed Update
        nudge = {"type": "noosphere_nudge", "magnitude": global_awareness, "target": "all_agents"}
        approved, reason = self.constitutional_gate.evaluate(None, torch.tensor(macro_state))
        
        if approved:
            protected = self.dp_wrapper.clip_and_add_noise([torch.tensor(a.genome) for a in self.agents])
            self._apply_fed_update(protected)
        
        # 7. Metrics
        metrics = {
            "noosphere_global_awareness": global_awareness,
            "noosphere_hierarchical_macros": len(macros),
            "noosphere_reality_entropy": np.abs(reality_layer[:,:,0]).mean() if self.reality_engine else 0.0,
            "noosphere_viral_spread": len(self.viral_buffer),
            "noosphere_approved_nudges": int(approved)
        }
        
        return metrics

    async def _propagate_viral_thought(self, coherence: float):
        """انتشار الفكرة/النودج بين العقد (Viral Propagation)"""
        if coherence > 0.7:
            thought = {
                "idea": f"coherent_thought_{len(self.viral_buffer)}",
                "strength": coherence,
                "timestamp": asyncio.get_event_loop().time()
            }
            self.viral_buffer.append(thought)
            # نشر لكل agent
            for agent in self.agents:
                agent.genome[24:32] += np.random.normal(0, 0.02 * coherence, 8)  # تأثير على reality match
            print(f"🦠 Viral Thought Spread | Strength: {coherence:.3f}")

    def _apply_fed_update(self, protected_gradients):
        """تطبيق التحديث الفيدرالي الآمن"""
        for agent in self.agents:
            agent.genome = 0.85 * agent.genome + 0.15 * protected_gradients[0].numpy()

    def get_full_state(self) -> Dict:
        """حالة Noosphere الكاملة (للـ Gradio / Grafana)"""
        return {
            "global_awareness": self.ogcg.awareness,
            "collective_reality_match": self.collective_reality_match(),
            "pollution_level": self.pollution_field.mean(),
            "mental_disorders_active": int(np.sum(self.mental_disorder_map > 0.3)),
            "active_lasers": sum(len(e.laser_beams) for e in self.envs),
            "hierarchical_macros": len(self.hierarchical_model.compress_agents(...)),  # placeholder
            "viral_thoughts": len(self.viral_buffer)
        }
