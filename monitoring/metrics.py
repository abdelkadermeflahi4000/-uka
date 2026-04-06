"""
📊 Đuka Metrics Collector - Prometheus Integration
يجمع مقاييس الأداء، الصحة، والتعلم من جميع الطبقات
"""

from prometheus_client import (
    Counter, Gauge, Histogram, Summary, 
    start_http_server, CollectorRegistry, generate_latest
)
import time
import psutil
import asyncio
from typing import Dict, Optional
from dataclasses import dataclass
import logging

logger = logging.getLogger("duka.metrics")


# ─────────────────────────────────────────────────────────────
# 📈 تعريف المقاييس (Metrics Definitions)
# ─────────────────────────────────────────────────────────────

class ĐukaMetrics:
    """مقاييس نظام Đuka الكاملة"""
    
    def __init__(self, node_id: str = "duka_node_01"):
        self.node_id = node_id
        self.registry = CollectorRegistry()
        
        # 🔄 Pipeline Performance
        self.cycle_counter = Counter(
            'duka_pipeline_cycles_total',
            'Total number of pipeline cycles executed',
            ['node_id', 'status'],
            registry=self.registry
        )
        
        self.cycle_latency = Histogram(
            'duka_pipeline_cycle_latency_seconds',
            'Latency of each pipeline cycle in seconds',
            ['node_id', 'layer'],
            buckets=[0.001, 0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0],
            registry=self.registry
        )
        
        self.layer_latency = Histogram(
            'duka_layer_latency_seconds',
            'Latency per individual layer',
            ['node_id', 'layer_name'],
            buckets=[0.001, 0.005, 0.01, 0.025, 0.05, 0.1],
            registry=self.registry
        )
        
        # 🧠 ML/AI Metrics
        self.model_reward = Gauge(
            'duka_model_reward',
            'Current model reward/return',
            ['node_id', 'model_name'],
            registry=self.registry
        )
        
        self.model_loss = Gauge(
            'duka_model_loss',
            'Current training/inference loss',
            ['node_id', 'model_name'],
            registry=self.registry
        )
        
        self.prediction_confidence = Histogram(
            'duka_prediction_confidence',
            'Confidence scores of predictions',
            ['node_id'],
            buckets=[0.1, 0.3, 0.5, 0.7, 0.8, 0.9, 0.95, 0.99],
            registry=self.registry
        )
        
        # 🌐 Network Metrics
        self.network_packets_sent = Counter(
            'duka_network_packets_sent_total',
            'Total knowledge packets sent',
            ['node_id', 'carrier_type'],
            registry=self.registry
        )
        
        self.network_packets_received = Counter(
            'duka_network_packets_received_total',
            'Total knowledge packets received',
            ['node_id', 'peer_id'],
            registry=self.registry
        )
        
        self.network_latency = Histogram(
            'duka_network_latency_seconds',
            'Network communication latency',
            ['node_id', 'peer_id'],
            buckets=[0.01, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5],
            registry=self.registry
        )
        
        self.knowledge_sync_score = Gauge(
            'duka_knowledge_sync_score',
            'Knowledge synchronization score with peers',
            ['node_id'],
            registry=self.registry
        )
        
        # 💻 System Resources
        self.cpu_usage = Gauge(
            'duka_system_cpu_usage_percent',
            'CPU usage percentage',
            ['node_id'],
            registry=self.registry
        )
        
        self.memory_usage = Gauge(
            'duka_system_memory_usage_bytes',
            'Memory usage in bytes',
            ['node_id'],
            registry=self.registry
        )
        
        self.gpu_usage = Gauge(
            'duka_system_gpu_usage_percent',
            'GPU usage percentage (if available)',
            ['node_id'],
            registry=self.registry
        )
        
        self.disk_usage = Gauge(
            'duka_system_disk_usage_percent',
            'Disk usage percentage',
            ['node_id', 'mount_point'],
            registry=self.registry
        )
        
        # ⚠️ Health & Errors
        self.error_counter = Counter(
            'duka_errors_total',
            'Total number of errors by layer',
            ['node_id', 'layer', 'error_type'],
            registry=self.registry
        )
        
        self.health_status = Gauge(
            'duka_health_status',
            'Health status of the node (1=healthy, 0=unhealthy)',
            ['node_id', 'component'],
            registry=self.registry
        )
        
        # 🎯 Decision Metrics
        self.decision_counter = Counter(
            'duka_decisions_total',
            'Total decisions made',
            ['node_id', 'action_type', 'safety_override'],
            registry=self.registry
        )
        
        self.execution_success_rate = Gauge(
            'duka_execution_success_rate',
            'Success rate of action executions',
            ['node_id'],
            registry=self.registry
        )
        
        logger.info(f"📊 Đuka Metrics initialized for node: {node_id}")
    
    # ─────────────────────────────────────────────────────────────
    # 📤 Methods لتحديث المقاييس
    # ─────────────────────────────────────────────────────────────
    
    def record_cycle_complete(self, status: str = "success"):
        """تسجيل دورة كاملة"""
        self.cycle_counter.labels(node_id=self.node_id, status=status).inc()
    
    def record_layer_latency(self, layer: str, latency_sec: float):
        """تسجيل زمن استجابة طبقة"""
        self.layer_latency.labels(
            node_id=self.node_id, 
            layer_name=layer
        ).observe(latency_sec)
    
    def record_prediction(self, confidence: float):
        """تسجيل تنبؤ مع مستوى ثقة"""
        self.prediction_confidence.labels(node_id=self.node_id).observe(confidence)
    
    def record_network_packet(self, direction: str, peer_id: str = "", carrier: str = "wifi"):
        """تسجيل حزمة شبكة"""
        if direction == "sent":
            self.network_packets_sent.labels(
                node_id=self.node_id, 
                carrier_type=carrier
            ).inc()
        elif direction == "received":
            self.network_packets_received.labels(
                node_id=self.node_id, 
                peer_id=peer_id
            ).inc()
    
    def record_network_latency(self, peer_id: str, latency_sec: float):
        """تسجيل زمن شبكة"""
        self.network_latency.labels(
            node_id=self.node_id, 
            peer_id=peer_id
        ).observe(latency_sec)
    
    def record_error(self, layer: str, error_type: str):
        """تسجيل خطأ"""
        self.error_counter.labels(
            node_id=self.node_id,
            layer=layer,
            error_type=error_type
        ).inc()
        self.health_status.labels(
            node_id=self.node_id, 
            component=layer
        ).set(0)
    
    def update_health(self, component: str, is_healthy: bool):
        """تحديث حالة الصحة"""
        self.health_status.labels(
            node_id=self.node_id, 
            component=component
        ).set(1 if is_healthy else 0)
    
    def update_system_resources(self):
        """تحديث مقاييس النظام"""
        self.cpu_usage.labels(node_id=self.node_id).set(psutil.cpu_percent(interval=1))
        self.memory_usage.labels(node_id=self.node_id).set(psutil.virtual_memory().used)
        
        disk = psutil.disk_usage('/')
        self.disk_usage.labels(
            node_id=self.node_id, 
            mount_point="/"
        ).set(disk.percent)
        
        # GPU (إذا وجدت)
        try:
            import torch
            if torch.cuda.is_available():
                gpu_usage = torch.cuda.utilization(0) if hasattr(torch.cuda, 'utilization') else 0
                self.gpu_usage.labels(node_id=self.node_id).set(gpu_usage)
        except ImportError:
            pass
    
    def update_ml_metrics(self, model_name: str, reward: float = None, loss: float = None):
        """تحديث مقاييس التعلم الآلي"""
        if reward is not None:
            self.model_reward.labels(
                node_id=self.node_id, 
                model_name=model_name
            ).set(reward)
        if loss is not None:
            self.model_loss.labels(
                node_id=self.node_id, 
                model_name=model_name
            ).set(loss)
    
    def record_decision(self, action_type: str, safety_override: bool = False):
        """تسجيل قرار"""
        self.decision_counter.labels(
            node_id=self.node_id,
            action_type=action_type,
            safety_override=str(safety_override).lower()
        ).inc()
    
    def get_metrics(self) -> str:
        """الحصول على جميع المقاييس بصيغة Prometheus"""
        return generate_latest(self.registry).decode('utf-8')


# ─────────────────────────────────────────────────────────────
# 🌐 Metrics HTTP Server
# ─────────────────────────────────────────────────────────────

class MetricsServer:
    """خادم HTTP لعرض المقاييس لـ Prometheus"""
    
    def __init__(self, metrics: ĐukaMetrics, port: int = 8000):
        self.metrics = metrics
        self.port = port
        self.is_running = False
    
    async def start(self):
        """بدء خادم المقاييس"""
        start_http_server(self.port, registry=self.metrics.registry)
        logger.info(f"📊 Metrics server started on port {self.port}")
        logger.info(f" Metrics endpoint: http://localhost:{self.port}/metrics")
        self.is_running = True
    
    async def stop(self):
        """إيقاف الخادم"""
        self.is_running = False
        logger.info("📊 Metrics server stopped")


# ─────────────────────────────────────────────────────────────
# 🔄 Resource Monitor Background Task
# ─────────────────────────────────────────────────────────────

async def resource_monitor(metrics: ĐukaMetrics, interval: float = 5.0):
    """مهمة خلفية لمراقبة موارد النظام"""
    while True:
        try:
            metrics.update_system_resources()
            await asyncio.sleep(interval)
        except Exception as e:
            logger.error(f"Error in resource monitor: {e}")
            await asyncio.sleep(interval)
