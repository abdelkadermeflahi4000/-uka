# src/network/message_bus.py
import asyncio
import json
import logging
from typing import Callable, Dict, Any, Optional
import nats

logger = logging.getLogger("đuka.network")

class DukaMessageBus:
    def __init__(self, servers: list[str] = ["nats://localhost:4222"]):
        self.servers = servers
        self.nc: Optional[nats.NATS] = None

    async def connect(self) -> None:
        self.nc = await nats.connect(
            servers=self.servers,
            name="đuka-node",
            reconnect_time_wait=2,
            max_reconnect_attempts=10
        )
        logger.info("✅ Connected to Đuka Message Bus (NATS)")

    async def publish(self, subject: str, payload: Dict[str, Any], headers: Optional[Dict[str, str]] = None) -> None:
        if not self.nc: raise RuntimeError("Message bus not connected")
        await self.nc.publish(subject, json.dumps(payload).encode(), headers=headers)

    async def subscribe(self, subject: str, callback: Callable, queue: Optional[str] = None) -> None:
        if not self.nc: raise RuntimeError("Message bus not connected")
        async def handler(msg):
            try:
                data = json.loads(msg.data.decode())
                await callback(data, msg)
            except Exception as e:
                logger.error(f"❌ Handler error on {subject}: {e}")
        await self.nc.subscribe(subject, queue=queue, cb=handler)
        logger.info(f"📡 Subscribed to {subject} (queue: {queue or 'standalone'})")

    async def request(self, subject: str, payload: Dict[str, Any], timeout: float = 2.0) -> Dict[str, Any]:
        if not self.nc: raise RuntimeError("Message bus not connected")
        resp = await self.nc.request(subject, json.dumps(payload).encode(), timeout=timeout)
        return json.loads(resp.data.decode())

    async def close(self) -> None:
        if self.nc:
            await self.nc.close()
