from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Any, Dict, Optional
from uuid import uuid4
import time

class ComponentType(Enum):
    CORE = auto()
    NET = auto()
    SIM = auto()
    BIO = auto()
    ROBOTICS = auto()

@dataclass
class ĐukaMessage:
    """الرسالة الموحدة بين جميع وحدات Đuka"""
    id: str = field(default_factory=lambda: str(uuid4()))
    timestamp: float = field(default_factory=time.time)
    source: str = ""  # component_id
    target: Optional[str] = None
    component: ComponentType = ComponentType.CORE
    msg_type: str = ""
    payload: Dict[str, Any] = field(default_factory=dict)
    priority: int = 5  # 1-10
    requires_ack: bool = False
    
    def to_bytes(self) -> bytes:
        import json
        return json.dumps(self.__dict__, default=str).encode()
    
    @classmethod
    def from_bytes(cls, data: bytes) -> 'ĐukaMessage':
        import json
        return cls(**json.loads(data.decode()))

class ĐukaCore:
    """المحرك المركزي الذي يربط كل المكونات"""
    
    def __init__(self, node_id: str):
        self.node_id = node_id
        self.components: Dict[ComponentType, Any] = {}
        self.message_queue: asyncio.Queue = asyncio.Queue()
        self.running = False
        
    def register(self, component_type: ComponentType, instance):
        """تسجيل مكون في النظام"""
        self.components[component_type] = instance
        instance._bind_core(self)  # ربط عكسي
        return self
        
    async def broadcast(self, message: ĐukaMessage, exclude: Optional[ComponentType] = None):
        """بث رسالة لكل المكونات المسجلة"""
        for ctype, comp in self.components.items():
            if ctype != exclude and hasattr(comp, 'on_message'):
                await comp.on_message(message)
    
    async def start(self):
        """بدء حلقة المعالجة الرئيسية"""
        self.running = True
        while self.running:
            msg = await self.message_queue.get()
            await self.broadcast(msg)
            self.message_queue.task_done()
    
    def stop(self):
        self.running = False
