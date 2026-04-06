import asyncio
from typing import Dict, List, Optional
from dataclasses import dataclass
from .transport import TransportLayer
from đuka_core import ĐukaMessage, ComponentType

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
        self.transport = TransportLayer(config.get('transport', 'websocket'))
        self.peers: Dict[str, PeerInfo] = {}
        self.routing_table: Dict[str, List[str]] = {}
        self._core = None
        
    def _bind_core(self, core):
        self._core = core
        
    async def connect(self, address: str) -> bool:
        """الاتصال بعقدة أخرى"""
        success = await self.transport.connect(address)
        if success:
            # تبادل معلومات العقد
            await self._exchange_peer_info()
        return success
        
    async def send(self, target_node: str, message: ĐukaMessage):
        """إرسال رسالة مع توجيه ذكي"""
        path = self._find_best_path(target_node)
        
        for hop in path:
            peer = self.peers.get(hop)
            if not peer:
                continue
            # محاكاة التأخير الشبكي
            if self.config.get('simulate_latency'):
                await asyncio.sleep(peer.latency_ms / 1000)
            await self.transport.send_to(hop, message.to_bytes())
    
    def _find_best_path(self, destination: str) -> List[str]:
        """خوارزمية توجيه مبسطة (يمكن تطويرها لـ A* أو Dijkstra)"""
        # TODO: implement proper routing
        return [destination] if destination in self.peers else []
        
    async def on_message(self, message: ĐukaMessage):
        """معالجة الرسائل الواردة من الشبكة"""
        # تمرير الرسالة للعقل المركزي
        if self._core:
            await self._core.message_queue.put(message)
