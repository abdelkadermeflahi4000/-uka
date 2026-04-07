--- demo_ai_integration.py (原始)


+++ demo_ai_integration.py (修改后)
"""
demo_ai_integration.py — مثال عملي لدمج الذكاء الاصطناعي التوليدي في Đuka Protocol

يوضح هذا المثال:
1. كيف تفسر الروبوتات بيانات مستشعراتها باستخدام AI
2. كيف تُخزن التفسيرات في ĐukaKnowledge
3. كيف تشارك الروبوتات المعرفة عبر الشبكة
"""
import asyncio
import logging
import time
from src.ai_interpreter import (
    AIInterpreter,
    SensorData,
    Interpretation,
    create_lidar_data,
    create_camera_data,
    create_imu_data,
    SensorType
)
from src.đuka_knowledge import ĐukaKnowledge, KnowledgeEntry, create_knowledge_entry

# إعداد التسجيل
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("đuka.demo")


async def demo_basic_interpretation():
    """مثال 1: تفسير أساسي لبيانات المستشعرات"""
    print("\n" + "="*60)
    print("🧪 المثال 1: تفسير بيانات المستشعرات")
    print("="*60)

    # إنشاء المترجم
    interpreter = AIInterpreter(model_name="gpt2", use_local=False)
    await interpreter.initialize()

    # بيانات LiDAR
    lidar_data = create_lidar_data(distance=2.3, direction="أمام", speed=0.5)
    lidar_data.robot_id = "robot_001"

    # تفسير البيانات
    interpretation = await interpreter.interpret(lidar_data)

    print(f"\n📡 بيانات LiDAR:")
    print(f"   المسافة: {lidar_data.data['distance']} متر")
    print(f"   الاتجاه: {lidar_data.data['direction']}")

    print(f"\n💡 التفسير:")
    print(f"   {interpretation.text}")
    print(f"   الثقة: {interpretation.confidence:.2f}")
    print(f"   الكلمات المفتاحية: {', '.join(interpretation.tags)}")

    return interpretation


async def demo_knowledge_storage():
    """مثال 2: تخزين التفسيرات في ĐukaKnowledge"""
    print("\n" + "="*60)
    print("🧪 المثال 2: تخزين المعرفة المشتركة")
    print("="*60)

    # إنشاء شبكة المعرفة
    knowledge_net = ĐukaKnowledge(node_id="node_alpha", max_entries=1000)

    # إنشاء مترجم
    interpreter = AIInterpreter(use_local=False)
    await interpreter.initialize()

    # محاكاة قراءات من عدة روبوتات
    robots = ["robot_001", "robot_002", "robot_003"]

    for robot_id in robots:
        # بيانات LiDAR
        lidar_data = create_lidar_data(
            distance=1.5 + len(robot_id) * 0.5,
            direction="أمام" if robot_id != "robot_002" else "يمين"
        )
        lidar_data.robot_id = robot_id

        # تفسير
        interpretation = await interpreter.interpret(lidar_data)

        # إنشاء مدخل معرفي
        entry = create_knowledge_entry(
            content=interpretation.text,
            source_robot=robot_id,
            tags=interpretation.tags,
            metadata={
                'sensor_type': 'LiDAR',
                'distance': lidar_data.data.get('distance'),
                'original_data': lidar_data.to_dict()
            },
            confidence=interpretation.confidence
        )

        # تخزين
        await knowledge_net.store(entry)

    # عرض الإحصائيات
    stats = knowledge_net.get_stats()
    print(f"\n📊 إحصائيات المعرفة:")
    print(f"   إجمالي المدخلات: {stats['total_entries']}")
    print(f"   الكلمات المفتاحية الفريدة: {stats['unique_tags']}")
    print(f"   الروبوتات المساهمة: {stats['unique_robots']}")
    print(f"   متوسط الثقة: {stats['avg_confidence']:.2f}")

    # البحث عن معرفة
    print(f"\n🔍 البحث عن كلمة 'عقبة':")
    results = await knowledge_net.search_by_tag('obstacle')
    for entry in results:
        print(f"   • [{entry.source_robot}] {entry.content[:60]}...")

    return knowledge_net


async def demo_multi_sensor_fusion():
    """مثال 3: دمج بيانات من مستشعرات متعددة"""
    print("\n" + "="*60)
    print("🧪 المثال 3: دمج بيانات مستشعرات متعددة")
    print("="*60)

    interpreter = AIInterpreter(use_local=False)
    await interpreter.initialize()

    # بيانات من مستشعرات مختلفة لنفس اللحظة
    timestamp = time.time()

    lidar = SensorData(
        sensor_type=SensorType.LIDAR,
        timestamp=timestamp,
        data={'distance': 3.2, 'direction': 'أمام'},
        robot_id='robot_001'
    )

    camera = SensorData(
        sensor_type=SensorType.CAMERA,
        timestamp=timestamp,
        data={'color': 'أحمر', 'object_type': 'صندوق', 'position': 'اليسار'},
        robot_id='robot_001'
    )

    imu = SensorData(
        sensor_type=SensorType.IMU,
        timestamp=timestamp,
        data={'angle': 5.2, 'acceleration': 0.3},
        robot_id='robot_001'
    )

    # تفسير كل مستشعر
    interpretations = await interpreter.interpret_batch([lidar, camera, imu])

    print(f"\n🤖 الروبوت robot_001 في الوقت {timestamp:.2f}:")
    for interp in interpretations:
        sensor_name = interp.sensor_data.sensor_type.name
        print(f"\n   [{sensor_name}]:")
        print(f"      {interp.text}")
        print(f"      الثقة: {interp.confidence:.2f}")

    # إنشاء وصف موحد
    combined_description = " | ".join([i.text for i in interpretations])
    print(f"\n📝 الوصف الموحد:")
    print(f"   {combined_description}")

    return interpretations


async def demo_knowledge_sharing():
    """مثال 4: مشاركة المعرفة بين الروبوتات"""
    print("\n" + "="*60)
    print("🧪 المثال 4: مشاركة المعرفة بين الروبوتات")
    print("="*60)

    # عقدتان للمعرفة (محاكاة لروبوتين)
    knowledge_a = ĐukaKnowledge(node_id="node_A", max_entries=500)
    knowledge_b = ĐukaKnowledge(node_id="node_B", max_entries=500)

    interpreter = AIInterpreter(use_local=False)
    await interpreter.initialize()

    # الروبوت A يكتشف شيئاً ويخزنه
    print(f"\n🤖 الروبوت A يكتشف عقبة...")
    lidar_a = create_lidar_data(distance=2.0, direction="أمام")
    lidar_a.robot_id = "robot_A"

    interp_a = await interpreter.interpret(lidar_a)
    entry_a = create_knowledge_entry(
        content=interp_a.text,
        source_robot="robot_A",
        tags=interp_a.tags,
        metadata={'location': 'corridor_1'}
    )
    await knowledge_a.store(entry_a)

    # الروبوت B يبحث عن معرفة ذات صلة
    print(f"\n🤖 الروبوت B يبحث عن معلومات حول 'عقبة'...")
    results = await knowledge_a.search_by_tag('obstacle')

    if results:
        print(f"   ✅ وُجدت {len(results)} مدخلات ذات صلة")

        # الروبوت B يستخدم هذه المعلومة
        for entry in results:
            print(f"   📖 من {entry.source_robot}: {entry.content}")

            # يمكن للروبوت B تعديل سلوكه بناءً على هذه المعلومة
            print(f"   ⚙️ الروبوت B يعدل مساره لتجنب العقبة!")

    return knowledge_a, knowledge_b


async def main():
    """تشغيل جميع الأمثلة"""
    print("\n" + "🌟"*30)
    print("🌐 Đuka Protocol - AI Integration Demo")
    print("🌟"*30)

    try:
        # تشغيل الأمثلة
        await demo_basic_interpretation()
        await demo_knowledge_storage()
        await demo_multi_sensor_fusion()
        await demo_knowledge_sharing()

        print("\n" + "="*60)
        print("✅ اكتملت جميع الأمثلة بنجاح!")
        print("="*60)
        print("\n💡 الخطوات التالية:")
        print("   1. دمج AI Interpreter مع ROS2 Bridge")
        print("   2. ربط ĐukaKnowledge بشبكة Mesh")
        print("   3. إضافة دعم للنماذج اللغوية الكبيرة (LLaMA, GPT-4)")
        print("   4. تطبيق التعلم الفيدرالي على التفسيرات")

    except Exception as e:
        logger.error(f"خطأ في التشغيل: {e}", exc_info=True)


if __name__ == "__main__":
    asyncio.run(main())