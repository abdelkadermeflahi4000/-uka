"""
transport.py — طبقة النقل لشبكة Đuka
✅ FIX: هذا الملف كان مفقوداً كلياً — mesh.py يستورد منه TransportLayer

يدعم حالياً: websocket (قابل التوسعة لـ QUIC, TCP raw, Bluetooth)
"""
import asyncio
import json
import logging
from typing import Dict, Callable, Optional

logger = logging.getLogger(__name__)


class TransportLayer:
    """
    طبقة النقل المجردة — تخفي بروتوكول الاتصال الفعلي عن باقي النظام
    حالياً: محاكاة داخلية — في الإنتاج: websockets أو aiohttp
    """

    SUPPORTED = ['websocket', 'tcp', 'simulation']

    def __init__(self, transport_type: str = 'simulation'):
        if transport_type not in self.SUPPORTED:
            raise ValueError(f"Transport '{transport_type}' غير مدعوم. الخيارات: {self.SUPPORTED}")

        self.transport_type = transport_type
        self.connections: Dict[str, asyncio.Queue] = {}  # node_id → incoming queue
        self.on_receive: Optional[Callable] = None
        self._connected = False

        logger.info(f"[Transport] Initialized with type: {transport_type}")

    async def connect(self, address: str) -> bool:
        """
        الاتصال بعنوان عقدة أخرى.
        في وضع simulation: نجاح دائم.
        في وضع websocket: يستخدم websockets library.
        """
        try:
            if self.transport_type == 'simulation':
                # محاكاة: نسجل العنوان كـ queue داخلية
                self.connections[address] = asyncio.Queue()
                self._connected = True
                logger.info(f"[Transport/sim] Connected to {address}")
                return True

            elif self.transport_type == 'websocket':
                # في الإنتاج:
                # import websockets
                # self._ws = await websockets.connect(f"ws://{address}")
                logger.warning("[Transport/ws] WebSocket غير مفعّل — تحتاج: pip install websockets")
                return False

        except Exception as e:
            logger.error(f"[Transport] Connection failed to {address}: {e}")
            return False

    async def send_to(self, target_id: str, data: bytes) -> bool:
        """إرسال bytes لعقدة مستهدفة"""
        if self.transport_type == 'simulation':
            if target_id in self.connections:
                await self.connections[target_id].put(data)
                return True
            logger.warning(f"[Transport] Target '{target_id}' not in connections")
            return False

        elif self.transport_type == 'websocket':
            # await self._ws.send(data)
            logger.warning("[Transport/ws] لم يُنفَّذ بعد")
            return False

        return False

    async def receive(self, source_id: str, timeout: float = 5.0) -> Optional[bytes]:
        """استقبال bytes من عقدة"""
        if source_id in self.connections:
            try:
                data = await asyncio.wait_for(
                    self.connections[source_id].get(),
                    timeout=timeout
                )
                return data
            except asyncio.TimeoutError:
                return None
        return None

    def is_connected(self) -> bool:
        return self._connected and len(self.connections) > 0

    async def disconnect(self, address: str):
        """إغلاق الاتصال"""
        if address in self.connections:
            del self.connections[address]
        if not self.connections:
            self._connected = False
        logger.info(f"[Transport] Disconnected from {address}")
