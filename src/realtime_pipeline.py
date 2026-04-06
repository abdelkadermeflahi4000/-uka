"""
⚡ Đuka Real-Time Cognitive Pipeline - 30Hz Strict Loop
دمج: Hierarchical + Surrogate + Constitutional + DP-Fed + Monitoring
"""
import asyncio
import time
import torch
import numpy as np
from typing import Dict, Any, Optional, List, Tuple
from dataclasses import dataclass
import logging
from pathlib import Path

# استيراد الطبقات المدمجة (مفصلة أدناه)
from src.layers.hierarchical_world import HierarchicalSurrogateModel
from src.layers.constitutional_gate import ConstitutionalDecisionGate
from src.layers.secure_feedback import SecureFeedbackLoop
from src.utils.realtime_sync import DeadlineEnforcer, FallbackPolicy
from monitoring.metrics import ĐukaMetrics, MetricsServer, resource_monitor
from monitoring.tensorboard_logger import ĐukaTensorBoardLogger

logging.basicConfig(level=logging.INFO, format="%(levelname)s [RT-PIPELINE] %(message)s")
logger = logging.getLogger("duka.realtime")

@dataclass
class RTConfig:
    target_hz: float = 30.0
    cycle_budget_ms: float = 33.33
    latency_warning_ms: float = 28.0
    fallback_threshold_ms: float = 32.0
    node_id: str = "duka_rt_01"
    enable_monitoring: bool = True
    dp_sync_interval_cycles: int = 10  # تحديث الخصوصية كل 10 دورات

class ĐukaRealTimePipeline:
    """
    ⚡ مشغِّل الحلقة الزمنية الحقيقية
    يضمن 30Hz عبر:
    - Pre-allocated Tensors
    - Deadline Enforcement
    - Async Background Tasks (DP, Audit, Network)
    - Degraded Fallback عند تجاوز الميزانية
    """
    def __init__(self, config: RTConfig = RTConfig()):
        self.cfg = config
        self.cycle_count = 0
        self.is_running = False
        self.deadline = DeadlineEnforcer(config.cycle_budget_ms, config.fallback_threshold_ms)
        self.fallback = FallbackPolicy()
        
        #  تهيئة الطبقات المدمجة
        self.world_model = HierarchicalSurrogateModel(device="cuda" if torch.cuda.is_available() else "cpu")
        self.decision_gate = ConstitutionalDecisionGuard(config.node_id)
        self.feedback_loop = SecureFeedbackLoop(dp_sync_interval=config.dp_sync_interval_cycles)
        
        #  مراقبة
        if config.enable_monitoring:
            self.metrics = ĐukaMetrics(node_id=config.node_id)
            self.tb_logger = ĐukaTensorBoardLogger(node_id=config.node_id)
            self.metrics_server = MetricsServer(self.metrics, port=8000)
            self.resource_task = None
        else:
            self.metrics = self.tb_logger = self.metrics_server = self.resource_task = None
            
        #  مخازن مسبقة التخصيص (Zero-Copy Hot Loop)
        self.state_buffer = torch.zeros(1, 12, device=self.world_model.device)
        self.action_buffer = torch.zeros(1, 4, device=self.world_model.device)
        
        logger.info(f"⚡ Đuka RT Pipeline initialized | Target: {config.target_hz}Hz | Budget: {config.cycle_budget_ms}ms")

    async def run_cycle(self, sensor_frame: Dict[str, Any]) -> Dict[str, Any]:
        """🔄 دورة إدراكية واحدة بحد زمني صارم"""
        t_start = time.perf_counter()
        self.deadline.reset()
        
        try:
            # 1. Perception → Tensor (Pre-allocated)
            self.state_buffer.copy_(torch.tensor(sensor_frame["state"], dtype=torch.float32).unsqueeze(0))
            
            # 2. Hierarchical World Model + Surrogate
            macro_state, sim_pred = await self.world_model.forward_async(self.state_buffer)
            self.deadline.checkpoint("world_model")
            
            # 3. Prediction (Causal RL Policy)
            action_logits = self.world_model.policy_network(self.state_buffer, macro_state)
            self.deadline.checkpoint("prediction")
            
            # 4. Constitutional Decision Gate
            decision, audit_hash = await self.decision_gate.evaluate(action_logits, macro_state)
            self.deadline.checkpoint("decision_gate")
            
            # 5. Execution (Nudge/Actuation)
            actuation_result = await self.feedback_loop.execute_nudge(decision, audit_hash)
            self.deadline.checkpoint("execution")
            
            # 6. Feedback + DP Queue
            await self.feedback_loop.queue_experience(
                state=self.state_buffer,
                action=action_logits,
                reward=actuation_result.get("reward", 0.0),
                next_state=sim_pred
            )
            self.deadline.checkpoint("feedback")
            
            #  تسجيل القياسات
            cycle_latency_ms = (time.perf_counter() - t_start) * 1000
            self._log_cycle_metrics(cycle_latency_ms, decision, actuation_result)
            
            return {
                "cycle": self.cycle_count,
                "latency_ms": cycle_latency_ms,
                "decision": decision["type"],
                "audit_hash": audit_hash,
                "status": "SUCCESS"
            }
            
        except Exception as e:
            cycle_latency_ms = (time.perf_counter() - t_start) * 1000
            logger.error(f"❌ Cycle {self.cycle_count} failed after {cycle_latency_ms:.2f}ms: {e}")
            self.fallback.activate()
            return {"cycle": self.cycle_count, "latency_ms": cycle_latency_ms, "status": "FALLBACK"}
        finally:
            self.cycle_count += 1

    async def run_continuous(self, sensor_stream: asyncio.Queue, max_cycles: int = 0):
        """🔁 تشغيل مستمر بـ 30Hz مع مزامنة زمنية"""
        self.is_running = True
        cycle_interval = 1.0 / self.cfg.target_hz
        
        # تشغيل المهام الخلفية
        if self.metrics_server:
            await self.metrics_server.start()
            self.resource_task = asyncio.create_task(resource_monitor(self.metrics, interval=5.0))
            
        dp_task = asyncio.create_task(self.feedback_loop.run_async_aggregation())
        
        logger.info(f"🚀 Starting 30Hz Real-Time Loop | Cycle Interval: {cycle_interval*1000:.1f}ms")
        
        try:
            while self.is_running:
                t_cycle_start = time.perf_counter()
                
                # استلام إطار مستشعر (غير متزامن مع الحلقة)
                if not sensor_stream.empty():
                    frame = await sensor_stream.get()
                    result = await self.run_cycle(frame)
                    sensor_stream.task_done()
                else:
                    result = await self.run_cycle({"state": self.state_buffer.squeeze().tolist()})
                
                # مزامنة زمنية صارمة
                elapsed = time.perf_counter() - t_cycle_start
                sleep_time = max(0, cycle_interval - elapsed)
                
                if sleep_time > 0:
                    await asyncio.sleep(sleep_time)
                else:
                    # تجاوز الميزانية → تسجيل تحذير
                    if self.metrics:
                        self.metrics.record_error("pipeline", "DEADLINE_EXCEEDED")
                    
                if max_cycles > 0 and self.cycle_count >= max_cycles:
                    break
                    
        finally:
            self.is_running = False
            dp_task.cancel()
            if self.resource_task: self.resource_task.cancel()
            if self.metrics_server: await self.metrics_server.stop()
            if self.tb_logger: self.tb_logger.close()
            logger.info("🛑 Real-Time Pipeline stopped gracefully.")

    def _log_cycle_metrics(self, latency_ms: float, decision: Dict, result: Dict):
        if not self.metrics: return
        self.metrics.record_cycle_complete("success")
        self.metrics.record_layer_latency("full_cycle", latency_ms/1000)
        self.metrics.record_prediction(decision.get("confidence", 0.0))
        self.tb_logger.log_pipeline_cycle(
            self.cycle_count, latency_ms,
            {"world": self.deadline.get_checkpoint("world_model"),
             "decision": self.deadline.get_checkpoint("decision_gate")},
            True
        )
