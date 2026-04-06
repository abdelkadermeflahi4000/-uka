import asyncio
import time
from typing import Dict, List, Optional
from dataclasses import dataclass

# ✅ FIX 1: from .transport كان يفترض package structure غير موجود
#           TransportLayer الآن في transport.py في نفس المستوى
from transport import TransportLayer

# ✅ FIX 2: đuka_core ليس module حقيقي — الكلاسات معرفة في protocol.py
from protocol import ĐukaMessage, ComponentType


@dataclass
class PeerInfo:
    node_id: str
    address: str
    capabilities: List[str]
    latency_ms: float
    last_seen: float


class ĐukaNet:
    """طبقة الشبكة الموزعة - تحاكي Starlink"""

    def __init__(self, node_id: str, config: dict):
        self.node_id = node_id
        self.config = config
        self.transport = TransportLayer(config.get('transport', 'simulation'))
        self.peers: Dict[str, PeerInfo] = {}
        self.routing_table: Dict[str, List[str]] = {}
        self._core = None

    def _bind_core(self, core):
        self._core = core

    async def connect(self, address: str) -> bool:
        """الاتصال بعقدة أخرى"""
        success = await self.transport.connect(address)
        if success:
            await self._exchange_peer_info(address)
        return success

    async def _exchange_peer_info(self, address: str):
        """
        تبادل بيانات العقدة بعد الاتصال.
        ✅ FIX: كانت المشكلة أن هذه الدالة مستدعاة لكن غير معرفة — رفعت AttributeError
        """
        peer = PeerInfo(
            node_id=address,
            address=address,
            capabilities=['relay', 'storage'],
            latency_ms=self.config.get('default_latency_ms', 50.0),
            last_seen=time.time()
        )
        self.peers[address] = peer
        # تحديث جدول التوجيه
        self.routing_table[address] = [address]

    async def send(self, target_node: str, message: ĐukaMessage):
        """إرسال رسالة مع توجيه ذكي"""
        path = self._find_best_path(target_node)

        if not path:
            return  # ✅ FIX: لا نرفع exception — نتجاهل إذا لا مسار

        for hop in path:
            peer = self.peers.get(hop)
            if not peer:
                continue
            # محاكاة التأخير الشبكي
            if self.config.get('simulate_latency'):
                await asyncio.sleep(peer.latency_ms / 1000)
            await self.transport.send_to(hop, message.to_bytes())

    def _find_best_path(self, destination: str) -> List[str]:
        """
        خوارزمية توجيه — حالياً مباشرة، قابلة للتطوير إلى Dijkstra
        ✅ حالة محسّنة: نبحث في routing_table أولاً
        """
        if destination in self.peers:
            return [destination]
        # بحث في routing_table عن مسار من hop واحد
        for via, path in self.routing_table.items():
            if destination in path:
                return [via, destination]
        return []

    async def on_message(self, message: ĐukaMessage):
        """معالجة الرسائل الواردة من الشبكة"""
        # تحديث last_seen للمُرسِل
        if message.source in self.peers:
            self.peers[message.source].last_seen = time.time()

        # تمرير الرسالة للعقل المركزي
        if self._core:
            await self._core.message_queue.put(message)

    def get_network_stats(self) -> dict:
        """إحصائيات الشبكة للمراقبة"""
        return {
            'node_id': self.node_id,
            'peers_count': len(self.peers),
            'avg_latency_ms': (
                sum(p.latency_ms for p in self.peers.values()) / len(self.peers)
                if self.peers else 0
            ),
            'routing_table_size': len(self.routing_table)
        }
