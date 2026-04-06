import rclpy  # ROS2 Python client library
from rclpy.node import Node
from std_msgs.msg import String, Float32MultiArray
from sensor_msgs.msg import Image, LaserScan
from đuka_core import ĐukaMessage, ComponentType

class ROS2Bridge(Node):
    """جسر بين Đuka و ROS2"""
    
    def __init__(self, node_name: str, đuka_core):
        super().__init__(node_name)
        self.core = đuka_core
        self.subscribers = {}
        self.publishers = {}
        
    def subscribe_to_ros(self, topic: str, msg_type, callback):
        """الاشتراك في موضوع ROS2 وتحويله لرسالة Đuka"""
        def ros_callback(msg):
            # تحويل رسالة ROS2 لـ ĐukaMessage
            đuka_msg = ĐukaMessage(
                source=f"ros2:{topic}",
                component=ComponentType.ROBOTICS,
                msg_type='sensor_data',
                payload={
                    'topic': topic,
                    'data': self._serialize_ros_msg(msg),
                    'timestamp': self.get_clock().now().nanoseconds / 1e9
                }
            )
            # إرسال للعقل المركزي
            asyncio.create_task(self.core.message_queue.put(đuka_msg))
            
        sub = self.create_subscription(msg_type, topic, ros_callback, 10)
        self.subscribers[topic] = sub
        
    def publish_to_ros(self, topic: str, msg_type, data: dict):
        """إرسال أمر من Đuka لـ ROS2"""
        if topic not in self.publishers:
            self.publishers[topic] = self.create_publisher(msg_type, topic, 10)
            
        ros_msg = self._deserialize_to_ros(msg_type, data)
        self.publishers[topic].publish(ros_msg)
        
    def _serialize_ros_msg(self, msg) -> dict:
        """تحويل رسالة ROS2 لـ dict قابل للإرسال"""
        # تبسيط: في الإنتاج نستخدم ROS2 introspection أو custom serializers
        if hasattr(msg, 'data'):
            return {'data': list(msg.data) if hasattr(msg.data, '__iter__') else msg.data}
        return str(msg)
        
    def _deserialize_to_ros(self, msg_type, data: dict):
        """تحويل dict لرسالة ROS2"""
        # تبسيط: يحتاج تنفيذ كامل حسب نوع الرسالة
        return msg_type(**data)

class RoboticsExecutor:
    """منفذ الأوامر مع طبقة أمان"""
    
    def __init__(self, robot_id: str, bio_module: 'ĐukaBio'):
        self.robot_id = robot_id
        self.bio = bio_module
        self.ros_bridge: Optional[ROS2Bridge] = None
        
    async def execute_command(self, command: dict) -> tuple[bool, str]:
        """تنفيذ أمر بعد التحقق الأخلاقي"""
        # 1️⃣ التحقق الأخلاقي أولاً
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
