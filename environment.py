import numpy as np
from typing import Dict, List, Optional
from đuka_core import ĐukaMessage, ComponentType

class SimulationEnvironment:
    """بيئة محاكاة قابلة للتوسعة"""
    
    def __init__(self, env_id: str, config: dict):
        self.env_id = env_id
        self.config = config
        self.time_scale: float = 1.0  # 1.0 = وقت حقيقي، 1000.0 = أسرع 1000 مرة
        self.entities: Dict[str, 'SimEntity'] = {}
        self._core = None
        
    def _bind_core(self, core):
        self._core = core
        
    def add_entity(self, entity_id: str, entity_type: str, properties: dict):
        """إضافة كيان للمحاكاة (روبوت، عائق، إنسان...)"""
        from .physics import PhysicsBody
        from .sensors import SensorArray
        
        entity = SimEntity(entity_id, entity_type, properties)
        entity.add_component(PhysicsBody(properties.get('physics', {})))
        entity.add_component(SensorArray(properties.get('sensors', [])))
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
            'timestamp': time.time(),
            'entities': {
                eid: ent.get_state() 
                for eid, ent in self.entities.items()
            }
        }
        msg = ĐukaMessage(
            source=self.env_id,
            component=ComponentType.SIM,
            msg_type='sim_state_update',
            payload=state
        )
        await self._core.message_queue.put(msg)

class SimEntity:
    """كيان داخل المحاكاة"""
    
    def __init__(self, entity_id: str, entity_type: str, properties: dict):
        self.id = entity_id
        self.type = entity_type
        self.properties = properties
        self.components: Dict[str, Any] = {}
        
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
            'position': self.components.get('physicsbody', {}).get_position(),
            'sensors': {
                name: comp.read() 
                for name, comp in self.components.items() 
                if hasattr(comp, 'read')
            }
        }
