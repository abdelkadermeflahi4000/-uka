"""
discovery.py — اكتشاف العقد تلقائياً على الشبكة المحلية
الآلية:
  1. كل عقدة تبث UDP broadcast كل 3 ثوانٍ على المنفذ 50000
  2. العقد الأخرى تستقبل وتسجّل العناوين تلقائياً
  3. عند اكتشاف عقدة جديدة → إشعار فوري للـ mesh
"""
import asyncio
import json
import socket
import logging
import time
from typing import Callable, Dict, Optional, Set

logger = logging.getLogger("đuka.discovery")

DISCOVERY_PORT = 50000
BROADCAST_INTERVAL = 3.0    # ثوانٍ بين كل broadcast
NODE_TIMEOUT = 15.0         # عقدة لم تُسمع منها → تُعتبر منفصلة


class NodeDiscovery:
    """
    اكتشاف تلقائي للعقد عبر UDP Broadcast على الشبكة المحلية
    """

    def __init__(self, node_id: str, ws_port: int, on_peer_found: Optional[Callable] = None):
        self.node_id = node_id
        self.ws_port = ws_port                      # منفذ WebSocket هذه العقدة
        self.on_peer_found = on_peer_found          # callback عند اكتشاف عقدة جديدة
        self.known_peers: Dict[str, dict] = {}      # node_id → {address, ws_port, last_seen}
        self._running = False

    # ─────────────────────────────────────────────
    # بث الوجود (Announce)
    # ─────────────────────────────────────────────
    async def _broadcast_presence(self):
        """يبث وجود هذه العقدة كل BROADCAST_INTERVAL ثانية"""
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        sock.setblocking(False)

        payload = json.dumps({
            "type": "đuka_announce",
            "node_id": self.node_id,
            "ws_port": self.ws_port,
            "timestamp": time.time()
        }).encode()

        loop = asyncio.get_event_loop()
        logger.info(f"[Discovery] 📡 بدء البث على منفذ {DISCOVERY_PORT}")

        while self._running:
            try:
                await loop.sock_sendto(sock, payload, ('<broadcast>', DISCOVERY_PORT))
                logger.debug(f"[Discovery] 📣 بثّ وجود {self.node_id}")
            except Exception as e:
                logger.warning(f"[Discovery] خطأ في البث: {e}")
            await asyncio.sleep(BROADCAST_INTERVAL)

        sock.close()

    # ─────────────────────────────────────────────
    # الاستماع للعقد الأخرى (Listen)
    # ─────────────────────────────────────────────
    async def _listen_for_peers(self):
        """يستمع لـ broadcasts من العقد الأخرى"""
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind(('', DISCOVERY_PORT))
        sock.setblocking(False)

        loop = asyncio.get_event_loop()
        logger.info(f"[Discovery] 👂 استماع على منفذ {DISCOVERY_PORT}")

        while self._running:
            try:
                data, addr = await loop.sock_recvfrom(sock, 1024)
                msg = json.loads(data.decode())

                if (msg.get('type') == 'đuka_announce'
                        and msg['node_id'] != self.node_id):     # لا نسجّل نفسنا
                    await self._handle_peer(msg, addr[0])

            except asyncio.CancelledError:
                break
            except Exception:
                await asyncio.sleep(0.1)

        sock.close()

    async def _handle_peer(self, msg: dict, ip_address: str):
        """معالجة إعلان عقدة مكتشفة"""
        peer_id = msg['node_id']
        ws_address = f"{ip_address}:{msg['ws_port']}"
        is_new = peer_id not in self.known_peers

        self.known_peers[peer_id] = {
            'node_id': peer_id,
            'ip': ip_address,
            'ws_address': ws_address,
            'ws_port': msg['ws_port'],
            'last_seen': time.time()
        }

        if is_new:
            logger.info(f"[Discovery] 🆕 عقدة جديدة مكتشفة: {peer_id} @ {ws_address}")
            if self.on_peer_found:
                await self.on_peer_found(peer_id, ws_address)
        else:
            logger.debug(f"[Discovery] 🔄 عقدة معروفة: {peer_id}")

    # ─────────────────────────────────────────────
    # مراقبة الانقطاعات (Watchdog)
    # ─────────────────────────────────────────────
    async def _watchdog(self):
        """يراقب العقد ويُزيل المنقطعة"""
        while self._running:
            now = time.time()
            disconnected = [
                pid for pid, info in self.known_peers.items()
                if now - info['last_seen'] > NODE_TIMEOUT
            ]
            for pid in disconnected:
                logger.warning(f"[Discovery] ⚠️ عقدة منقطعة: {pid}")
                del self.known_peers[pid]
            await asyncio.sleep(5.0)

    # ─────────────────────────────────────────────
    # التشغيل والإيقاف
    # ─────────────────────────────────────────────
    async def start(self):
        self._running = True
        await asyncio.gather(
            self._broadcast_presence(),
            self._listen_for_peers(),
            self._watchdog(),
            return_exceptions=True
        )

    def stop(self):
        self._running = False

    def get_peers(self) -> Dict[str, dict]:
        return dict(self.known_peers)

    def peer_count(self) -> int:
        return len(self.known_peers)
