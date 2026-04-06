"""
transport.py — طبقة النقل الحقيقية عبر WebSocket
يدعم: websocket (حقيقي) + simulation (اختبار محلي)
"""
import asyncio
import json
import logging
from typing import Dict, Callable, Optional

logger = logging.getLogger("đuka.transport")


class TransportLayer:
    SUPPORTED = ['websocket', 'simulation']

    def __init__(self, transport_type: str = 'websocket'):
        if transport_type not in self.SUPPORTED:
            raise ValueError(f"Transport '{transport_type}' غير مدعوم.")
        self.transport_type = transport_type
        self.connections: Dict[str, any] = {}   # address → websocket object
        self._sim_queues: Dict[str, asyncio.Queue] = {}
        self.on_receive: Optional[Callable] = None
        logger.info(f"[Transport] نوع النقل: {transport_type}")

    # ─────────────────────────────────────────────
    # الاتصال
    # ─────────────────────────────────────────────
    async def connect(self, address: str) -> bool:
        try:
            if self.transport_type == 'websocket':
                import websockets
                ws = await websockets.connect(f"ws://{address}", ping_interval=20)
                self.connections[address] = ws
                logger.info(f"[Transport/ws] ✅ اتصال بـ {address}")
                # مستمع في الخلفية
                asyncio.create_task(self._ws_listener(address, ws))
                return True

            elif self.transport_type == 'simulation':
                self._sim_queues[address] = asyncio.Queue()
                self.connections[address] = address
                logger.info(f"[Transport/sim] ✅ محاكاة اتصال بـ {address}")
                return True

        except Exception as e:
            logger.error(f"[Transport] ❌ فشل الاتصال بـ {address}: {e}")
            return False

    # ─────────────────────────────────────────────
    # الإرسال
    # ─────────────────────────────────────────────
    async def send_to(self, address: str, data: bytes) -> bool:
        try:
            if self.transport_type == 'websocket':
                ws = self.connections.get(address)
                if ws:
                    await ws.send(data)
                    return True

            elif self.transport_type == 'simulation':
                q = self._sim_queues.get(address)
                if q:
                    await q.put(data)
                    return True

        except Exception as e:
            logger.error(f"[Transport] ❌ فشل الإرسال إلى {address}: {e}")
            # محاولة إعادة الاتصال
            self.connections.pop(address, None)
        return False

    # ─────────────────────────────────────────────
    # الاستقبال (WebSocket)
    # ─────────────────────────────────────────────
    async def _ws_listener(self, address: str, ws):
        """يستمع لرسائل واردة من عقدة معينة"""
        try:
            async for raw in ws:
                if self.on_receive:
                    await self.on_receive(address, raw if isinstance(raw, bytes) else raw.encode())
        except Exception as e:
            logger.warning(f"[Transport] انقطع الاتصال مع {address}: {e}")
            self.connections.pop(address, None)

    async def receive(self, address: str, timeout: float = 5.0) -> Optional[bytes]:
        """استقبال في وضع simulation فقط"""
        q = self._sim_queues.get(address)
        if q:
            try:
                return await asyncio.wait_for(q.get(), timeout=timeout)
            except asyncio.TimeoutError:
                return None
        return None

    def is_connected(self, address: str = None) -> bool:
        if address:
            return address in self.connections
        return len(self.connections) > 0

    async def disconnect(self, address: str):
        ws = self.connections.pop(address, None)
        if ws and self.transport_type == 'websocket':
            await ws.close()
        self._sim_queues.pop(address, None)
        logger.info(f"[Transport] انقطع الاتصال مع {address}")
