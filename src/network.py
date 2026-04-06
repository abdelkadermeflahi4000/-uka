"""
🛰️ Đuka Network Layer - Virtual Starlink Simulation
محاكاة لشبكة موزعة لتبادل المعرفة بين الروبوتات/العقد
"""

import asyncio
import json
from typing import Dict, List, Optional, Callable
from dataclasses import dataclass, field, asdict
from datetime import datetime
import numpy as np


@dataclass
class KnowledgePacket:
    """📦 حزمة معرفة قابلة للإرسال عبر الشبكة"""
    sender_id: str
    timestamp: float
    experience_data: Dict
    model_weights_hash: str
    confidence: float = 1.0
    
    def to_json(self) -> str:
        return json.dumps(asdict(self), default=str)
    
    @classmethod
    def from_json(cls, json_str: str) -> "KnowledgePacket":
        data = json.loads(json_str)
        return cls(**data)


class VirtualStarlinkNode:
    """
    🛰️ عقدة في شبكة Đuka الموزعة
    """
    
    def __init__(self, node_id: str, latency_ms: float = 50.0):
        self.node_id = node_id
        self.latency_ms = latency_ms  # محاكاة زمن الانتقال
        self.peers: Dict[str, "VirtualStarlinkNode"] = {}
        self.knowledge_buffer: List[KnowledgePacket] = []
        self.on_receive: Optional[Callable] = None
        
    def connect(self, peer: "VirtualStarlinkNode"):
        """🔗 إنشاء اتصال مع عقدة أخرى"""
        self.peers[peer.node_id] = peer
        peer.peers[self.node_id] = self
        print(f"🔗 [{self.node_id}] ↔ [{peer.node_id}]")
    
    async def send_knowledge(self, packet: KnowledgePacket, target: Optional[str] = None):
        """📡 إرسال حزمة معرفة (محاكاة غير متزامنة)"""
        targets = [target] if target else list(self.peers.keys())
        
        for peer_id in targets:
            if peer_id in self.peers:
                # محاكاة زمن الانتقال
                await asyncio.sleep(self.latency_ms / 1000)
                
                # إضافة ضوضاء واقعية للقناة
                received_packet = self._simulate_channel_noise(packet)
                
                # تسليم للعقدة المستلمة
                await self.peers[peer_id]._receive_packet(received_packet)
                
                print(f"📤 [{self.node_id}] → [{peer_id}] | Confidence: {packet.confidence:.2f}")
    
    def _simulate_channel_noise(self, packet: KnowledgePacket) -> KnowledgePacket:
        """📡 محاكاة ضوضاء قناة الاتصال (واقعية)"""
        # تقليل الثقة بنسبة طفيفة عشوائية
        noise_factor = np.random.uniform(0.98, 1.0)
        packet.confidence *= noise_factor
        return packet
    
    async def _receive_packet(self, packet: KnowledgePacket):
        """📥 استقبال حزمة معرفة"""
        self.knowledge_buffer.append(packet)
        print(f"📥 [{self.node_id}] Received from [{packet.sender_id}]")
        
        if self.on_receive:
            await self.on_receive(packet)
    
    def process_buffer(self) -> List[KnowledgePacket]:
        """🔄 معالجة الحزم المستلمة واسترجاعها"""
        packets = self.knowledge_buffer.copy()
        self.knowledge_buffer.clear()
        return packets
    
    def broadcast(self, packet: KnowledgePacket):
        """📢 بث حزمة معرفة لكل الـ Peers"""
        return asyncio.gather(*[
            self.send_knowledge(packet, peer_id) 
            for peer_id in self.peers.keys()
        ])


class ĐukaNetwork:
    """
    🌐 مدير شبكة Đuka الكامل
    """
    
    def __init__(self):
        self.nodes: Dict[str, VirtualStarlinkNode] = {}
    
    def add_node(self, node_id: str, latency_ms: float = 50.0) -> VirtualStarlinkNode:
        """➕ إضافة عقدة جديدة للشبكة"""
        node = VirtualStarlinkNode(node_id, latency_ms)
        self.nodes[node_id] = node
        return node
    
    def create_mesh(self, node_ids: List[str], connectivity: float = 0.7):
        """🕸️ إنشاء شبكة Mesh بعشوائية متحكم بها"""
        nodes = [self.add_node(nid) for nid in node_ids]
        
        for i, node in enumerate(nodes):
            for j, other in enumerate(nodes[i+1:], start=i+1):
                if np.random.random() < connectivity:
                    node.connect(other)
        
        print(f"🕸️ Mesh created: {len(nodes)} nodes, {sum(len(n.peers) for n in nodes)//2} links")
    
    async def run_simulation(self, duration_steps: int = 10):
        """🔄 تشغيل محاكاة لتبادل المعرفة"""
        for step in range(duration_steps):
            print(f"\n🔁 Step {step + 1}/{duration_steps}")
            
            for node in self.nodes.values():
                # إنشاء حزمة معرفة وهمية
                packet = KnowledgePacket(
                    sender_id=node.node_id,
                    timestamp=datetime.now().timestamp(),
                    experience_data={"reward": np.random.uniform(0, 1), "steps": step},
                    model_weights_hash=f"hash_{np.random.randint(10000):05d}",
                    confidence=1.0
                )
                
                # بث المعرفة
                await node.broadcast(packet)
            
            await asyncio.sleep(0.1)  # فاصل زمني بين الخطوات
        
        # عرض الإحصائيات
        self._print_stats()
    
    def _print_stats(self):
        """📊 عرض إحصائيات الشبكة"""
        print("\n📊 Network Statistics:")
        for node_id, node in self.nodes.items():
            print(f"  [{node_id}] Peers: {len(node.peers)}, Buffered: {len(node.knowledge_buffer)}")
