"""
mesh.py — شبكة Đuka الموزعة
WebSocket حقيقي + اكتشاف تلقائي للعقد + Dijkstra routing
"""
import asyncio
import time
import heapq
import logging
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field

import websockets
from websockets.server import WebSocketServerProtocol

from transport import TransportLayer
from protocol import ĐukaMessage, ComponentType
from discovery import NodeDiscovery

logger = logging.getLogger("đuka.mesh")


@dataclass
class PeerInfo:
    node_id: str
    ws_address: str         # "ip:port"
    capabilities: List[str] = field(default_factory=list)
    latency_ms: float = 50.0
    last_seen: float = field(default_factory=time.time)
    hops: int = 1           # عدد القفزات من هذه العقدة


class ĐukaNet:
    """
    طبقة الشبكة الموزعة
    - WebSocket server يستقبل اتصالات الآخرين
    - UDP discovery يكتشف العقد تلقائياً
    - Dijkstra routing لإيجاد أفضل مسار
    """

    def __init__(self, node_id: str, config: dict):
        self.node_id = node_id
        self.config = config
        self.ws_port: int = config.get('ws_port', 8765)
        self.transport = TransportLayer(config.get('transport', 'websocket'))
        self.peers: Dict[str, PeerInfo] = {}
        # graph: node_id → {neighbor_id: latency_ms}
        self._graph: Dict[str, Dict[str, float]] = {node_id: {}}
        self._core = None
        self._ws_server = None
        self._discovery: Optional[NodeDiscovery] = None

    def _bind_core(self, core):
        self._core = core

    # ─────────────────────────────────────────────
    # WebSocket Server (يستقبل اتصالات الآخرين)
    # ─────────────────────────────────────────────
    async def start_server(self):
        """يشغّل WebSocket server على ws_port"""
        self._ws_server = await websockets.serve(
            self._handle_incoming,
            "0.0.0.0",
            self.ws_port
        )
        logger.info(f"[Mesh] 🟢 WebSocket server شغّال على منفذ {self.ws_port}")

        # تشغيل Discovery في الخلفية
        self._discovery = NodeDiscovery(
            node_id=self.node_id,
            ws_port=self.ws_port,
            on_peer_found=self._on_peer_discovered
        )
        asyncio.create_task(self._discovery.start())
        logger.info(f"[Mesh] 📡 Discovery نشط — أبحث عن عقد أخرى...")

    async def _handle_incoming(self, ws: WebSocketServerProtocol, path: str):
        """معالجة اتصال وارد من عقدة أخرى"""
        peer_addr = f"{ws.remote_address[0]}:{ws.remote_address[1]}"
        logger.info(f"[Mesh] 🔗 اتصال وارد من {peer_addr}")

        try:
            async for raw in ws:
                data = raw if isinstance(raw, bytes) else raw.encode()
                await self._process_incoming(data, peer_addr)
        except websockets.exceptions.ConnectionClosed:
            logger.info(f"[Mesh] انقطع الاتصال مع {peer_addr}")

    # ─────────────────────────────────────────────
    # Discovery Callback — اتصال تلقائي
    # ─────────────────────────────────────────────
    async def _on_peer_discovered(self, peer_id: str, ws_address: str):
        """عند اكتشاف عقدة جديدة → اتصال فوري"""
        if peer_id in self.peers:
            return

        logger.info(f"[Mesh] 🤝 محاولة الاتصال بـ {peer_id} @ {ws_address}")
        t0 = time.time()
        success = await self.transport.connect(ws_address)
        latency = (time.time() - t0) * 1000

        if success:
            peer = PeerInfo(
                node_id=peer_id,
                ws_address=ws_address,
                capabilities=['relay', 'learning'],
                latency_ms=latency
            )
            self.peers[peer_id] = peer
            self._graph[self.node_id][peer_id] = latency
            self._graph.setdefault(peer_id, {})[self.node_id] = latency

            logger.info(f"[Mesh] ✅ متصل بـ {peer_id} | latency: {latency:.1f}ms")

            # إرسال رسالة ترحيب
            hello = ĐukaMessage(
                source=self.node_id,
                component=ComponentType.NET,
                msg_type='hello',
                payload={
                    'node_id': self.node_id,
                    'capabilities': ['relay', 'learning'],
                    'ws_port': self.ws_port
                }
            )
            await self.transport.send_to(ws_address, hello.to_bytes())

    # ─────────────────────────────────────────────
    # الإرسال مع Dijkstra Routing
    # ─────────────────────────────────────────────
    async def send(self, target_node: str, message: ĐukaMessage):
        """إرسال رسالة — يجد أفضل مسار تلقائياً"""
        if target_node == self.node_id:
            return

        path = self._dijkstra(target_node)
        if not path:
            logger.warning(f"[Mesh] لا مسار إلى {target_node}")
            return

        logger.debug(f"[Mesh] مسار إلى {target_node}: {' → '.join(path)}")

        # إرسال للخطوة الأولى فقط (hop-by-hop relay)
        next_hop = path[0]
        peer = self.peers.get(next_hop)
        if peer:
            if self.config.get('simulate_latency'):
                await asyncio.sleep(peer.latency_ms / 1000)
            await self.transport.send_to(peer.ws_address, message.to_bytes())

    def _dijkstra(self, destination: str) -> List[str]:
        """
        Dijkstra لإيجاد أقصر مسار بناءً على الـ latency
        Returns: قائمة العقد من الجار الأول حتى الوجهة (بدون self)
        """
        if destination not in self._graph:
            # وجهة مباشرة أو غير معروفة
            return [destination] if destination in self.peers else []

        # (تكلفة, عقدة, المسار)
        heap = [(0.0, self.node_id, [])]
        visited: Dict[str, float] = {}

        while heap:
            cost, node, path = heapq.heappop(heap)
            if node in visited:
                continue
            visited[node] = cost
            path = path + [node]

            if node == destination:
                # نُرجع المسار بدون نقطة البداية (self)
                return path[1:]

            for neighbor, latency in self._graph.get(node, {}).items():
                if neighbor not in visited:
                    heapq.heappush(heap, (cost + latency, neighbor, path))

        return []

    # ─────────────────────────────────────────────
    # معالجة الرسائل الواردة
    # ─────────────────────────────────────────────
    async def _process_incoming(self, data: bytes, from_addr: str):
        try:
            msg = ĐukaMessage.from_bytes(data)
        except Exception as e:
            logger.error(f"[Mesh] رسالة تالفة من {from_addr}: {e}")
            return

        # تحديث last_seen
        for peer in self.peers.values():
            if peer.ws_address.startswith(from_addr.split(':')[0]):
                peer.last_seen = time.time()

        # Relay: إذا الرسالة مش لنا → نُمررها
        if msg.target and msg.target != self.node_id:
            await self.send(msg.target, msg)
            return

        # معالجة رسائل الشبكة الداخلية
        if msg.msg_type == 'hello':
            await self._handle_hello(msg)
            return

        if msg.msg_type == 'ping':
            pong = ĐukaMessage(
                source=self.node_id,
                target=msg.source,
                component=ComponentType.NET,
                msg_type='pong',
                payload={'echo': msg.payload}
            )
            peer = self.peers.get(msg.source)
            if peer:
                await self.transport.send_to(peer.ws_address, pong.to_bytes())
            return

        # رسالة للعقل المركزي
        if self._core:
            await self._core.message_queue.put(msg)

    async def _handle_hello(self, msg: ĐukaMessage):
        """تسجيل عقدة جديدة من رسالة hello"""
        payload = msg.payload
        peer_id = payload.get('node_id', msg.source)
        if peer_id and peer_id not in self.peers:
            logger.info(f"[Mesh] 👋 hello من {peer_id}")

    async def on_message(self, message: ĐukaMessage):
        """رسائل من ĐukaCore للشبكة"""
        if message.target:
            await self.send(message.target, message)

    # ─────────────────────────────────────────────
    # إحصائيات
    # ─────────────────────────────────────────────
    def get_network_stats(self) -> dict:
        return {
            'node_id': self.node_id,
            'peers': [
                {
                    'id': p.node_id,
                    'address': p.ws_address,
                    'latency_ms': round(p.latency_ms, 2),
                    'last_seen': round(time.time() - p.last_seen, 1)
                }
                for p in self.peers.values()
            ],
            'graph_nodes': len(self._graph),
            'discovery_active': self._discovery is not None
        }

    def stop(self):
        if self._ws_server:
            self._ws_server.close()
        if self._discovery:
            self._discovery.stop()
