"""
📡 Đuka Resonance Layer - الجسر بين المنطق والموجة
يعمل كـ Adapter بين "One Solution Logic" و"الناقل الفيزيائي"
"""

import numpy as np
from enum import Enum, auto
from dataclasses import dataclass
from typing import Optional, Callable, Dict, Union
import asyncio


class CarrierType(Enum):
    """أنواع الحوامل المدعومة"""
    WIFI = auto()
    LORA = auto()
    SDR_ELF = auto()      # Experimental: 3-30 Hz
    SDR_VLF = auto()      # 3-30 kHz
    CEMI_BIO = auto()     # نظري: مجال كهرومغناطيسي حيوي
    OPTICAL = auto()      # LiFi / Laser


@dataclass
class ResonancePacket:
    """📦 حزمة معرفة مُشفَّرة ترددياً"""
    payload: Dict                    # البيانات الأساسية
    semantic_hash: str              # بصمة المعنى (من One Solution)
    carrier: CarrierType            # نوع الحامل
    frequency_hz: float             # التردد الحامل
    modulation: str = "QPSK"        # نوع التشكيل
    bio_signature: Optional[str] = None  # توقيع حيوي (لـ CEMI)
    temporal_marker: Optional[float] = None  # علامة زمنية (لفكرة الاشتباك الزماني)
    
    def to_waveform(self, sample_rate: int = 44100) -> np.ndarray:
        """🔊 تحويل الحزمة إلى شكل موجي (للتجريب/المحاكاة)"""
        # محاكاة بسيطة: نستخدم payload hash لتوليد ترددات فرعية
        duration = 0.1  # ثانية
        t = np.linspace(0, duration, int(sample_rate * duration), endpoint=False)
        
        # تردد حامل + تعديل طوري بسيط بناءً على البيانات
        phase_mod = np.sum([ord(c) for c in self.semantic_hash[:8]]) / 100
        waveform = np.sin(2 * np.pi * self.frequency_hz * t + phase_mod)
        
        # إضافة "بصمة معنى" كضوضاء منظمة (للمحاكاة فقط)
        meaning_noise = np.random.normal(0, 0.01, len(t)) * (ord(self.semantic_hash[0]) / 255)
        return waveform + meaning_noise


class ResonanceRouter:
    """
    🧭 موجِّه الرنين: يقرر أي حامل يستخدم لأي نوع من "المعنى"
    يحاكي فكرة "التردد يناسب النية" من إطار One Solution
    """
    
    # خريطة تجريبية: نوع المعنى → التردد الأمثل
    SEMANTIC_FREQUENCY_MAP = {
        "urgent_control": (CarrierType.SDR_VLF, 16_000),   # تحكم عاجل: VLF لموثوقية عالية
        "knowledge_sync": (CarrierType.WIFI, 2_400_000_000), # مزامنة معرفة: نطاق عريض
        "bio_feedback": (CarrierType.CEMI_BIO, 40.0),       # تغذية راجعة حيوية: ~40Hz (Gamma)
        "temporal_echo": (CarrierType.SDR_ELF, 7.83),       # صدى زماني: تردد شومان! 🌍
        "ambient_sense": (CarrierType.LORA, 868_000_000),   # استشعار محيطي: LoRa لمسافات طويلة
    }
    
    def __init__(self, node_id: str):
        self.node_id = node_id
        self.carriers: Dict[CarrierType, Callable] = {}
        self.on_receive: Optional[Callable[[ResonancePacket], None]] = None
        
    def register_carrier(self, carrier: CarrierType, handler: Callable):
        """تسجيل معالج لحامل معين"""
        self.carriers[carrier] = handler
        print(f"🔌 [{self.node_id}] Registered {carrier.name}")
    
    def route(self, packet: ResonancePacket) -> bool:
        """🚦 توجيه الحزمة للحامل المناسب"""
        if packet.carrier not in self.carriers:
            print(f"⚠️ [{self.node_id}] No handler for {packet.carrier.name}")
            return False
        
        # محاكاة إرسال (في التطبيق الحقيقي: SDR / Socket / ROS2 Topic)
        asyncio.create_task(self._simulate_transmit(packet))
        return True
    
    async def _simulate_transmit(self, packet: ResonancePacket):
        """📡 محاكاة عملية الإرسال مع خصائص فيزيائية"""
        # زمن انتقال يعتمد على التردد (محاكاة فيزيائية مبسطة)
        latency = max(0.001, 1000 / packet.frequency_hz)  # كلما انخفض التردد، زاد الزمن
        
        await asyncio.sleep(latency)
        
        # "تشويه" طفيف يحاكي ضوضاء القناة (واقعية)
        received_packet = self._apply_channel_effects(packet)
        
        if self.on_receive:
            self.on_receive(received_packet)
        
        print(f"📤→📥 [{self.node_id}] {packet.carrier.name}@{packet.frequency_hz/1e6:.2f}MHz | "
              f"Semantic: {packet.semantic_hash[:8]}...")
    
    def _apply_channel_effects(self, packet: ResonancePacket) -> ResonancePacket:
        """🌊 محاكاة تأثيرات القناة الفيزيائية على "المعنى" """
        # في تطبيق حقيقي: هنا ندمج نماذج فيزيائية حقيقية
        # الآن: نطبق "تدهور ثقة" بسيط يعتمد على التردد
        import random
        confidence_loss = random.uniform(0, 0.02) * (1e6 / packet.frequency_hz)
        
        # نضيف "صدى زماني" إذا كانت العلامة موجودة (لفكرة الاشتباك)
        if packet.temporal_marker:
            # محاكاة: المعنى القديم يتفاعل مع الحاضر
            time_delta = abs(packet.temporal_marker - asyncio.get_event_loop().time())
            if time_delta < 1.0:  # ضمن نافذة زمنية ضيقة
                packet.payload["temporal_resonance"] = True
        
        return packet
    
    @classmethod
    def suggest_carrier(cls, semantic_intent: str) -> tuple[CarrierType, float]:
        """🎯 اقتراح حامل وتردد بناءً على "نية المعنى" """
        # في One Solution: النية تحدد التردد
        # هنا: نستخدم مطابقة نصية بسيطة (قابلة للتطوير بـ AI)
        for key, (carrier, freq) in cls.SEMANTIC_FREQUENCY_MAP.items():
            if key in semantic_intent.lower():
                return carrier, freq
        # افتراضي: نختار الأكثر كفاءة للطاقة
        return CarrierType.LORA, 868_000_000
