import time                          # ✅ FIX: كان مفقوداً — _broadcast_state تستخدم time.time()
import numpy as np
from typing import Dict, List, Optional, Any   # ✅ FIX: Any كان مفقوداً — SimEntity.components تستخدمه

# ✅ FIX: đuka_core ليس module حقيقي
from protocol import ĐukaMessage, ComponentType


class SimulationEnvironment:
    """بيئة محاكاة قابلة للتوسعة"""

    def __init__(self, env_id: str, config: dict):
        self.env_id = env_id
        self.config = config
        self.time_scale: float = config.get('time_scale', 1.0)   # ✅ FIX: أخذ time_scale من config
        self.entities: Dict[str, 'SimEntity'] = {}
        self._core = None

    def _bind_core(self, core):
        self._core = core

    def add_entity(self, entity_id: str, entity_type: str, properties: dict):
        """إضافة كيان للمحاكاة (روبوت، عائق، إنسان...)"""
        # ✅ FIX: PhysicsBody و SensorArray لا وجود لهما — تم استبدالهما بـ stub آمن
        #         حتى لا يرفع ImportError عند التشغيل
        entity = SimEntity(entity_id, entity_type, properties)
        self.entities[entity_id] = entity
        return entity

    async def step(self, delta_time: float):
        """تحديث خطوة واحدة في المحاكاة"""
        actual_dt = delta_time * self.time_scale

        for entity in self.entities.values():
            await entity.update(actual_dt)

        # إرسال تحديثات للشبكة إذا لزم
        if self._core and self.config.get('sync_with_network'):
            await self._broadcast_state()

    async def _broadcast_state(self):
        """مشاركة حالة المحاكاة مع العقد الأخرى"""
        state = {
            'env_id': self.env_id,
            'timestamp': time.time(),       # ✅ يعمل الآن
            'entities': {
                eid: ent.get_state()
                for eid, ent in self.entities.items()
            }
        }
        msg = ĐukaMessage(                  # ✅ يعمل الآن
            source=self.env_id,
            component=ComponentType.SIM,
            msg_type='sim_state_update',
            payload=state
        )
        await self._core.message_queue.put(msg)

    async def on_message(self, message: ĐukaMessage):
        """معالجة الرسائل الواردة — مطلوب للتسجيل في ĐukaCore"""
        if message.msg_type == 'sim_command':
            cmd = message.payload.get('command')
            entity_id = message.payload.get('entity_id')
            if cmd == 'add_entity' and entity_id:
                self.add_entity(
                    entity_id,
                    message.payload.get('entity_type', 'generic'),
                    message.payload.get('properties', {})
                )


class SimEntity:
    """كيان داخل المحاكاة"""

    def __init__(self, entity_id: str, entity_type: str, properties: dict):
        self.id = entity_id
        self.type = entity_type
        self.properties = properties
        self.components: Dict[str, Any] = {}           # ✅ Any يعمل الآن
        self.position = properties.get('position', [0.0, 0.0, 0.0])

    def add_component(self, component):
        name = component.__class__.__name__.lower()
        self.components[name] = component
        return self

    async def update(self, delta_time: float):
        for comp in self.components.values():
            if hasattr(comp, 'update'):
                await comp.update(delta_time)

    def get_state(self) -> dict:
        return {
            'id': self.id,
            'type': self.type,
            'position': self.position,
            'properties': self.properties,
        }
