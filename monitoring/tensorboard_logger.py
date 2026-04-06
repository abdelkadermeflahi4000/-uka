"""
📈 Đuka TensorBoard Logger - ML Metrics Visualization
يسجل مقاييس التعلم العميق والتدريب لـ TensorBoard
"""

from torch.utils.tensorboard import SummaryWriter
import numpy as np
import time
from typing import Dict, Optional, Any
import logging
from pathlib import Path

logger = logging.getLogger("duka.tensorboard")


class ĐukaTensorBoardLogger:
    """مسجل متكامل لـ TensorBoard"""
    
    def __init__(
        self, 
        log_dir: str = "logs/duka",
        node_id: str = "duka_node_01",
        flush_secs: int = 10
    ):
        self.node_id = node_id
        self.log_dir = Path(log_dir) / node_id / f"run_{time.strftime('%Y%m%d_%H%M%S')}"
        self.writer = SummaryWriter(
            log_dir=str(self.log_dir),
            flush_secs=flush_secs
        )
        self.global_step = 0
        logger.info(f"📈 TensorBoard logger initialized: {self.log_dir}")
    
    # ─────────────────────────────────────────────────────────────
    # 📊 Logging Methods
    # ─────────────────────────────────────────────────────────────
    
    def log_scalar(self, tag: str, value: float, step: Optional[int] = None):
        """تسجيل قيمة عددية"""
        if step is None:
            step = self.global_step
        self.writer.add_scalar(f"{self.node_id}/{tag}", value, step)
    
    def log_scalars(self, main_tag: str, tag_value_dict: Dict[str, float], step: Optional[int] = None):
        """تسجيل عدة قيم دفعة واحدة"""
        if step is None:
            step = self.global_step
        full_dict = {f"{self.node_id}/{k}": v for k, v in tag_value_dict.items()}
        self.writer.add_scalars(main_tag, full_dict, step)
    
    def log_histogram(self, tag: str, values: np.ndarray, step: Optional[int] = None):
        """تسجيل توزيع (Histogram)"""
        if step is None:
            step = self.global_step
        self.writer.add_histogram(f"{self.node_id}/{tag}", values, step)
    
    def log_image(self, tag: str, image: np.ndarray, step: Optional[int] = None):
        """تسجيل صورة (من Perception Layer)"""
        if step is None:
            step = self.global_step
        # image should be in CHW format for TensorBoard
        self.writer.add_image(f"{self.node_id}/{tag}", image, step)
    
    def log_video(self, tag: str, video: np.ndarray, step: Optional[int] = None, fps: int = 30):
        """تسجيل فيديو (من Simulation)"""
        if step is None:
            step = self.global_step
        self.writer.add_video(f"{self.node_id}/{tag}", video, step, fps=fps)
    
    def log_text(self, tag: str, text: str, step: Optional[int] = None):
        """تسجيل نص (مثل Decision Rationale)"""
        if step is None:
            step = self.global_step
        self.writer.add_text(f"{self.node_id}/{tag}", text, step)
    
    def log_graph(self, model):
        """تسجيل بنية النموذج"""
        try:
            # يحتاج dummy input
            self.writer.add_graph(model)
        except Exception as e:
            logger.warning(f"Could not log model graph: {e}")
    
    # ─────────────────────────────────────────────────────────────
    #  Pipeline-Specific Logging
    # ─────────────────────────────────────────────────────────────
    
    def log_pipeline_cycle(
        self,
        cycle_num: int,
        latency_ms: float,
        layer_latencies: Dict[str, float],
        success: bool
    ):
        """تسجيل دورة Pipeline كاملة"""
        self.log_scalar("pipeline/latency_ms", latency_ms, cycle_num)
        self.log_scalar("pipeline/success", 1.0 if success else 0.0, cycle_num)
        
        for layer, latency in layer_latencies.items():
            self.log_scalar(f"pipeline/layers/{layer}_latency_ms", latency, cycle_num)
        
        self.global_step = cycle_num
    
    def log_perception(
        self,
        cycle_num: int,
        num_objects: int,
        confidence: float,
        image: Optional[np.ndarray] = None
    ):
        """تسجيل مخرجات Perception"""
        self.log_scalar("perception/num_objects", num_objects, cycle_num)
        self.log_scalar("perception/confidence", confidence, cycle_num)
        
        if image is not None:
            self.log_image("perception/sample_image", image, cycle_num)
    
    def log_prediction(
        self,
        cycle_num: int,
        predicted_reward: float,
        risk_score: float,
        confidence: float,
        num_trajectories: int
    ):
        """تسجيل مخرجات Prediction"""
        self.log_scalars("prediction/metrics", {
            "predicted_reward": predicted_reward,
            "risk_score": risk_score,
            "confidence": confidence,
            "num_trajectories": num_trajectories
        }, cycle_num)
    
    def log_decision(
        self,
        cycle_num: int,
        action_type: str,
        rationale: str,
        safety_override: bool,
        confidence: float
    ):
        """تسجيل القرار المتخذ"""
        self.log_scalar("decision/confidence", confidence, cycle_num)
        self.log_scalar("decision/safety_override", 1.0 if safety_override else 0.0, cycle_num)
        self.log_text("decision/rationale", rationale, cycle_num)
    
    def log_execution(
        self,
        cycle_num: int,
        success: bool,
        latency_ms: float,
        telemetry: Dict
    ):
        """تسجيل نتيجة التنفيذ"""
        self.log_scalar("execution/success", 1.0 if success else 0.0, cycle_num)
        self.log_scalar("execution/latency_ms", latency_ms, cycle_num)
    
    def log_network_sync(
        self,
        cycle_num: int,
        peers_connected: int,
        sync_score: float,
        packets_sent: int,
        packets_received: int
    ):
        """تسجيل مزامنة الشبكة"""
        self.log_scalars("network/sync", {
            "peers_connected": peers_connected,
            "sync_score": sync_score,
            "packets_sent": packets_sent,
            "packets_received": packets_received
        }, cycle_num)
    
    def log_training(
        self,
        step: int,
        loss: float,
        reward: float,
        learning_rate: float,
        gradients: Optional[np.ndarray] = None
    ):
        """تسجيل مقاييس التدريب"""
        self.log_scalars("training/metrics", {
            "loss": loss,
            "reward": reward,
            "learning_rate": learning_rate
        }, step)
        
        if gradients is not None:
            self.log_histogram("training/gradients", gradients, step)
    
    def close(self):
        """إغلاق الـ Writer"""
        self.writer.close()
        logger.info("📈 TensorBoard writer closed")
