"""
ros2_bridge.py — جسر Đuka ↔ ROS2
✅ يعمل فقط عند وجود ROS2 مُهيأ. في حالة غيابه: يُنبّه ولا يرفع exception.
"""
import asyncio          # ✅ FIX: كان مفقوداً — asyncio.create_task مستخدم
from typing import Optional, Dict   # ✅ FIX: Optional كان مفقوداً

# ✅ FIX: đuka_core ليس module حقيقي
from protocol import ĐukaMessage, ComponentType

# ROS2 اختياري — لا يُوقف البرنامج إذا لم يكن مُثبتاً
try:
    import rclpy
    from rclpy.node import Node
    from std_msgs.msg import String, Float32MultiArray
    from sensor_msgs.msg import Image, LaserScan
    ROS2_AVAILABLE = True
except ImportError:
    ROS2_AVAILABLE = False
    # ✅ FIX: بدلاً من الفشل الصامت، نعرّف stub واضح
    class Node:
        def __init__(self, *args, **kwargs): pass
    print("⚠️ [ROS2Bridge] rclpy غير مُثبت — وحدة الروبوتات في وضع محاكاة")


class ROS2Bridge(Node):
    """جسر بين Đuka و ROS2"""

    def __init__(self, node_name: str, đuka_core):
        if ROS2_AVAILABLE:
            super().__init__(node_name)
        self.core = đuka_core
        self.subscribers: Dict = {}
        self.publishers: Dict = {}

    def subscribe_to_ros(self, topic: str, msg_type, callback):
        """الاشتراك في موضوع ROS2 وتحويله لرسالة Đuka"""
        if not ROS2_AVAILABLE:
            print(f"⚠️ [ROS2Bridge] تعذّر الاشتراك في {topic} — ROS2 غير متاح")
            return

        def ros_callback(msg):
            đuka_msg = ĐukaMessage(     # ✅ ĐukaMessage مستورد الآن
                source=f"ros2:{topic}",
                component=ComponentType.ROBOTICS,
                msg_type='sensor_data',
                payload={
                    'topic': topic,
                    'data': self._serialize_ros_msg(msg),
                    'timestamp': self.get_clock().now().nanoseconds / 1e9
                }
            )
            asyncio.create_task(self.core.message_queue.put(đuka_msg))  # ✅ asyncio مستورد

        sub = self.create_subscription(msg_type, topic, ros_callback, 10)
        self.subscribers[topic] = sub

    def publish_to_ros(self, topic: str, msg_type, data: dict):
        """إرسال أمر من Đuka لـ ROS2"""
        if not ROS2_AVAILABLE:
            print(f"⚠️ [ROS2Bridge] تعذّر النشر على {topic} — ROS2 غير متاح")
            return

        if topic not in self.publishers:
            self.publishers[topic] = self.create_publisher(msg_type, topic, 10)
        ros_msg = self._deserialize_to_ros(msg_type, data)
        self.publishers[topic].publish(ros_msg)

    def _serialize_ros_msg(self, msg) -> dict:
        if hasattr(msg, 'data'):
            return {'data': list(msg.data) if hasattr(msg.data, '__iter__') else msg.data}
        return {'raw': str(msg)}

    def _deserialize_to_ros(self, msg_type, data: dict):
        return msg_type(**data)


class RoboticsExecutor:
    """منفذ الأوامر مع طبقة أمان أخلاقية"""

    def __init__(self, robot_id: str, bio_module: Optional[object] = None):
        self.robot_id = robot_id
        self.bio = bio_module   # ĐukaBio — اختياري
        self.ros_bridge: Optional[ROS2Bridge] = None
        self._core = None

    def _bind_core(self, core):
        self._core = core

    async def execute_command(self, command: dict) -> tuple:
        """تنفيذ أمر بعد التحقق الأخلاقي"""
        # 1️⃣ التحقق الأخلاقي أولاً
        if self.bio:
            is_safe, reason = self.bio.validate_action({
                'action_type': command.get('type'),
                'parameters': command.get('params'),
                'decision_impact': command.get('impact_score', 0.5),
                'data_type': command.get('data_type')
            })
            if not is_safe:
                return False, f"🚫 Ethics Block: {reason}"

        # 2️⃣ تنفيذ الأمر عبر ROS2
        if self.ros_bridge:
            try:
                self.ros_bridge.publish_to_ros(
                    command['topic'],
                    command['msg_type'],
                    command['params']
                )
                return True, "✅ Executed"
            except Exception as e:
                return False, f"❌ Execution Error: {e}"

        return False, "⚠️ No ROS2 bridge connected"

    async def on_message(self, message: ĐukaMessage):
        """معالجة أوامر الروبوتات"""
        if message.msg_type == 'robot_command':
            ok, result = await self.execute_command(message.payload)
            print(f"[Robotics] {message.source} → {result}")
