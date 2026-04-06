# src/ros2_optimus_bridge.py
import rclpy
from rclpy.node import Node
from std_msgs.msg import Float64MultiArray

class OptimusROS2Bridge(Node):
    def __init__(self):
        super().__init__('duka_optimus_bridge')
        self.publisher = self.create_publisher(Float64MultiArray, '/joint_commands', 10)
    
    def publish_frequency_commands(self, frequency_vector: np.ndarray):
        msg = Float64MultiArray()
        msg.data = frequency_vector.tolist()  # [freq1, phase1, amp1, ...]
        self.publisher.publish(msg)
