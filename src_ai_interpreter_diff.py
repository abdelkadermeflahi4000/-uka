--- src/ai_interpreter.py (原始)


+++ src/ai_interpreter.py (修改后)
"""
ai_interpreter.py — مترجم الذكاء الاصطناعي التوليدي لبيانات الروبوتات
تحويل البيانات الحسية (LiDAR، Camera، IMU) إلى تفسيرات نصية مفهومة
"""
import asyncio
import json
import logging
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from enum import Enum, auto
import time

logger = logging.getLogger("đuka.ai_interpreter")


class SensorType(Enum):
    LIDAR = auto()
    CAMERA = auto()
    IMU = auto()
    DEPTH = auto()
    TACTILE = auto()
    AUDIO = auto()


@dataclass
class SensorData:
    """حزمة بيانات مستشعر خام"""
    sensor_type: SensorType
    timestamp: float = field(default_factory=time.time)
    data: Dict[str, Any] = field(default_factory=dict)
    robot_id: str = ""

    def to_dict(self) -> dict:
        return {
            'sensor_type': self.sensor_type.name,
            'timestamp': self.timestamp,
            'data': self.data,
            'robot_id': self.robot_id
        }


@dataclass
class Interpretation:
    """تفسير نصي لبيانات المستشعر"""
    text: str
    confidence: float
    sensor_data: SensorData
    timestamp: float = field(default_factory=time.time)
    interpretation_id: str = ""
    tags: List[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            'text': self.text,
            'confidence': self.confidence,
            'sensor_data': self.sensor_data.to_dict(),
            'timestamp': self.timestamp,
            'interpretation_id': self.interpretation_id,
            'tags': self.tags
        }


class AIInterpreter:
    """
    مترجم الذكاء الاصطناعي التوليدي

    يقوم بتحويل بيانات المستشعرات الخام إلى تفسيرات نصية مفهومة
    يمكن تخزينها في ĐukaKnowledge ومشاركتها عبر الشبكة
    """

    def __init__(self, model_name: str = "gpt2", use_local: bool = True):
        """
        Args:
            model_name: اسم النموذج اللغوي (gpt2, llama, gpt3.5-turbo, etc.)
            use_local: إذا True يستخدم نموذج محلي، وإلا يستخدم API خارجي
        """
        self.model_name = model_name
        self.use_local = use_local
        self.model = None
        self.tokenizer = None
        self._initialized = False

        # قوالب التفسير المسبقة (للنماذج الصغيرة أو عند عدم التوفر)
        self.templates = {
            SensorType.LIDAR: [
                "عقبة مكتشفة على بعد {distance} متر في اتجاه {direction}",
                "مسار واضح لمسافة {distance} متر",
                "كائن متحرك على بعد {distance} متر بسرعة {speed} م/ث"
            ],
            SensorType.CAMERA: [
                "كائن {color} {object_type} مكتشف في {position}",
                "حركة مكتشفة: {motion_description}",
                "إشارة مرور {state} على بعد {distance} متر"
            ],
            SensorType.IMU: [
                "الروبوت يميل بزاوية {angle} درجة",
                "تسارع مفاجئ: {acceleration} م/ث²",
                "اهتزاز غير طبيعي مكتشف"
            ],
            SensorType.DEPTH: [
                "سطح غير مستوٍ بارتفاع {height} سم",
                "منحدر بزاوية {slope} درجة",
                "حافة خطرة على بعد {distance} متر"
            ]
        }

    async def initialize(self):
        """تهيئة النموذج اللغوي"""
        if self._initialized:
            return

        if self.use_local:
            try:
                from transformers import pipeline, AutoTokenizer, AutoModelForCausalLM
                import torch

                logger.info(f"جاري تحميل النموذج {self.model_name}...")

                # تحميل النموذج والتوكينايزر
                if self.model_name in ["gpt2", "gpt2-medium", "gpt2-large"]:
                    self.generator = pipeline(
                        "text-generation",
                        model=self.model_name,
                        device=-1 if not torch.cuda.is_available() else 0
                    )
                else:
                    # نماذج أخرى مثل LLaMA
                    self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
                    self.model = AutoModelForCausalLM.from_pretrained(
                        self.model_name,
                        device_map="auto" if torch.cuda.is_available() else None
                    )

                self._initialized = True
                logger.info(f"✅ النموذج {self.model_name} جاهز للاستخدام")

            except ImportError:
                logger.warning("مكتبة transformers غير مثبتة — سأستخدم القوالب الجاهزة")
                self.use_local = False
                self._initialized = True
            except Exception as e:
                logger.error(f"خطأ في تحميل النموذج: {e}")
                self._initialized = True
        else:
            # استخدام API خارجي (OpenAI مثلاً)
            logger.info("سيتم استخدام API خارجي للتفسير")
            self._initialized = True

    async def interpret(self, sensor_data: SensorData, context: Optional[str] = None) -> Interpretation:
        """
        تحويل بيانات المستشعر إلى تفسير نصي

        Args:
            sensor_data: بيانات المستشعر الخام
            context: سياق إضافي (مثل حالة الروبوت السابقة)

        Returns:
            Interpretation: التفسير النصي مع مستوى الثقة
        """
        if not self._initialized:
            await self.initialize()

        # بناء الـ Prompt
        prompt = self._build_prompt(sensor_data, context)

        # توليد التفسير
        if self.use_local and self.model is not None:
            interpretation_text = await self._generate_with_model(prompt)
            confidence = 0.85  # ثقة تقديرية
        elif self.use_local and hasattr(self, 'generator'):
            interpretation_text = await self._generate_with_pipeline(prompt)
            confidence = 0.80
        else:
            # استخدام القوالب الجاهزة
            interpretation_text = self._generate_with_template(sensor_data)
            confidence = 0.65

        # إنشاء كائن التفسير
        import uuid
        interpretation = Interpretation(
            text=interpretation_text,
            confidence=confidence,
            sensor_data=sensor_data,
            interpretation_id=str(uuid.uuid4()),
            tags=self._extract_tags(interpretation_text)
        )

        logger.debug(f"🧠 تفسير: {interpretation_text[:100]}...")
        return interpretation

    def _build_prompt(self, sensor_data: SensorData, context: Optional[str]) -> str:
        """بناء Prompt مناسب للنموذج اللغوي"""
        base_prompts = {
            SensorType.LIDAR: """
أنت مساعد ذكي يفسر بيانات LiDAR من روبوت.
بيانات المستشعر: {data}
{context}
اكتب وصفاً واضحاً ومختصراً بالعربية للمشهد:""",

            SensorType.CAMERA: """
أنت مساعد ذكي يفسر صوراً من كاميرا روبوت.
بيانات المستشعر: {data}
{context}
اكتب وصفاً واضحاً ومختصراً بالعربية للمشهد:""",

            SensorType.IMU: """
أنت مساعد ذكي يفسر بيانات حركة من IMU.
بيانات المستشعر: {data}
{context}
اكتب وصفاً واضحاً ومختصراً بالعربية لحالة الحركة:""",

            SensorType.DEPTH: """
أنت مساعد ذكي يفسر بيانات عمق من كاميرا Depth.
بيانات المستشعر: {data}
{context}
اكتب وصفاً واضحاً ومختصراً بالعربية للتضاريس:"""
        }

        prompt_template = base_prompts.get(
            sensor_data.sensor_type,
            "فسر بيانات الروبوت التالية:\n{data}\n{context}"
        )

        context_str = f"السياق: {context}" if context else ""

        return prompt_template.format(
            data=json.dumps(sensor_data.data, ensure_ascii=False),
            context=context_str
        )

    async def _generate_with_pipeline(self, prompt: str) -> str:
        """التوليد باستخدام pipeline من Hugging Face"""
        try:
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(
                None,
                lambda: self.generator(prompt, max_length=100, num_return_sequences=1)[0]['generated_text']
            )
            # استخراج الجزء الجديد فقط
            generated = result[len(prompt):].strip()
            return generated if generated else "تم التحليل بنجاح"
        except Exception as e:
            logger.error(f"خطأ في التوليد: {e}")
            return "خطأ في تفسير البيانات"

    async def _generate_with_model(self, prompt: str) -> str:
        """التوليد باستخدام نموذج كامل"""
        try:
            import torch
            loop = asyncio.get_event_loop()

            def generate():
                inputs = self.tokenizer(prompt, return_tensors="pt")
                if torch.cuda.is_available():
                    inputs = {k: v.cuda() for k, v in inputs.items()}

                outputs = self.model.generate(
                    **inputs,
                    max_new_tokens=50,
                    num_return_sequences=1,
                    do_sample=True,
                    temperature=0.7
                )

                return self.tokenizer.decode(outputs[0], skip_special_tokens=True)

            result = await loop.run_in_executor(None, generate)
            generated = result[len(prompt):].strip()
            return generated if generated else "تم التحليل بنجاح"

        except Exception as e:
            logger.error(f"خطأ في التوليد: {e}")
            return "خطأ في تفسير البيانات"

    def _generate_with_template(self, sensor_data: SensorData) -> str:
        """توليد تفسير باستخدام القوالب الجاهزة"""
        templates = self.templates.get(sensor_data.sensor_type, ["بيانات مستشعر: {data}"])

        # اختيار قالب عشوائي وملء البيانات
        import random
        template = random.choice(templates)

        data = sensor_data.data

        # محاولة ملء المتغيرات في القالب
        try:
            interpretation = template.format(
                distance=data.get('distance', 'غير معروف'),
                direction=data.get('direction', 'غير معروف'),
                speed=data.get('speed', 'غير معروف'),
                color=data.get('color', 'غير معروف'),
                object_type=data.get('object_type', 'كائن'),
                position=data.get('position', 'المشهد'),
                motion_description=data.get('motion', 'حركة'),
                state=data.get('state', 'غير معروف'),
                angle=data.get('angle', 'غير معروف'),
                acceleration=data.get('acceleration', 'غير معروف'),
                height=data.get('height', 'غير معروف'),
                slope=data.get('slope', 'غير معروف')
            )
        except KeyError:
            interpretation = f"بيانات {sensor_data.sensor_type.name}: {json.dumps(data)}"

        return interpretation

    def _extract_tags(self, text: str) -> List[str]:
        """استخراج كلمات مفتاحية من التفسير"""
        # كلمات مفتاحية شائعة في سياق الروبوتات
        keywords = {
            'عقبة': 'obstacle',
            'حركة': 'motion',
            'كائن': 'object',
            'خطر': 'danger',
            'آمن': 'safe',
            'مسار': 'path',
            'إشارة': 'signal',
            'منحدر': 'slope',
            'حافة': 'edge'
        }

        tags = []
        for arabic, english in keywords.items():
            if arabic in text:
                tags.append(english)
                tags.append(arabic)

        return tags

    async def interpret_batch(self, sensor_data_list: List[SensorData]) -> List[Interpretation]:
        """تفسير مجموعة من قراءات المستشعرات"""
        tasks = [self.interpret(data) for data in sensor_data_list]
        return await asyncio.gather(*tasks)


# دوال مساعدة لإنشاء SensorData بسهولة
def create_lidar_data(distance: float, direction: str = "أمام", speed: Optional[float] = None) -> SensorData:
    """إنشاء بيانات LiDAR نموذجية"""
    data = {'distance': distance, 'direction': direction}
    if speed is not None:
        data['speed'] = speed
    return SensorData(sensor_type=SensorType.LIDAR, data=data)


def create_camera_data(color: str, object_type: str, position: str = "المركز") -> SensorData:
    """إنشاء بيانات Camera نموذجية"""
    return SensorData(
        sensor_type=SensorType.CAMERA,
        data={'color': color, 'object_type': object_type, 'position': position}
    )


def create_imu_data(angle: float = 0.0, acceleration: float = 0.0) -> SensorData:
    """إنشاء بيانات IMU نموذجية"""
    return SensorData(
        sensor_type=SensorType.IMU,
        data={'angle': angle, 'acceleration': acceleration}
    )