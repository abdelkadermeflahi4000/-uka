import rclpy
from rclpy.node import Node
from std_msgs.msg import Float64MultiArray, String
from sensor_msgs.msg import JointState
from trajectory_msgs.msg import JointTrajectory, JointTrajectoryPoint
import numpy as np
import asyncio
import time
from typing import Dict, List, Optional

# Đuka imports
from src.noosphere_expanded import ExpandedNoosphere
from src.ogcg.global_consciousness import GlobalConsciousness
from src.optimus_frequency_bridge import OptimusFrequencyBridge  # النسخة القديمة للتوافق
from src.layers.constitutional_gate import ConstitutionalDecisionGate


class OptimusROS2Bridge(Node):
    """
    🚀 Đuka Optimus ROS2 Bridge - كامل ومتكامل مع Noosphere + OGCG
    يدعم: Frequency Control + Laser Sync + Swarm Coordination
    """
    def __init__(self, noosphere: ExpandedNoosphere, node_name: str = "duka_optimus_bridge"):
        super().__init__(node_name)
        
        self.noosphere = noosphere
        self.ogcg = noosphere.ogcg
        self.frequency_bridge = OptimusFrequencyBridge()  # PyBullet fallback
        
        # Publishers
        self.joint_cmd_pub = self.create_publisher(Float64MultiArray, '/joint_commands', 10)
        self.trajectory_pub = self.create_publisher(JointTrajectory, '/joint_trajectory_controller/joint_trajectory', 10)
        self.laser_pub = self.create_publisher(String, '/duka_laser_command', 10)  # للـ silent rays
        
        # Subscriber للـ feedback
        self.joint_state_sub = self.create_subscription(
            JointState, '/joint_states', self.joint_state_callback, 10)
        
        # Timer لـ 30Hz cycle
        self.create_timer(1.0/30.0, self.run_bridge_cycle)
        
        self.current_joint_states = np.zeros(28)  # Optimus Gen2/3 ~28 DoF
        self.last_coherence = 0.0
        self.guardrail = ConstitutionalDecisionGate(node_id="optimus_bridge")
        
        self.get_logger().info("✅ Đuka Optimus ROS2 Bridge جاهز | متكامل مع Noosphere v2 + OGCG")

    def joint_state_callback(self, msg: JointState):
        """استقبال حالة المفاصل الحقيقية"""
        try:
            self.current_joint_states = np.array(msg.position)
        except:
            pass

    async def run_bridge_cycle(self):
        """الدورة الرئيسية 30Hz"""
        # 1. قراءة Global Awareness من Noosphere
        global_awareness = self.ogcg.awareness
        self.last_coherence = global_awareness
        
        # 2. استخراج macro state من Noosphere
        agent_states = np.array([a.genome for a in self.noosphere.agents])
        macro_state = agent_states.mean(axis=0) if len(agent_states) > 0 else np.zeros(12)
        
        # 3. Frequency Field → Joint Commands
        frequency_field = self.noosphere.envs[0].frequency_field if hasattr(self.noosphere, 'envs') else np.zeros((20,20))
        noosphere_field = self.noosphere.noosphere_field
        
        # توليد أوامر المفاصل (modulated by frequency + awareness)
        joint_commands = self._generate_frequency_commands(frequency_field, noosphere_field, global_awareness)
        
        # 4. Constitutional Validation + Guardrail
        nudge = {
            "type": "optimus_joint_nudge",
            "magnitude": global_awareness,
            "target": "full_body",
            "expected_effect": {"coordination": global_awareness * 0.9}
        }
        approved, reason = self.guardrail.evaluate(None, torch.tensor(macro_state))
        
        if approved:
            # 5. نشر الأوامر
            self._publish_joint_commands(joint_commands)
            
            # 6. Laser/Silent Rays Sync
            if global_awareness > 0.75:
                self._publish_laser_command(global_awareness)
            
            self.get_logger().info(f"🤖 Optimus Cycle | Awareness: {global_awareness:.3f} | Approved")
        else:
            self.get_logger().warning(f"🚫 Guardrail blocked: {reason}")

    def _generate_frequency_commands(self, freq_field: np.ndarray, noo_field: np.ndarray, awareness: float) -> np.ndarray:
        """تحويل الترددات + الوعي إلى أوامر مفاصل"""
        num_joints = 28  # Optimus approximate DoF
        commands = np.zeros(num_joints)
        
        for j in range(num_joints):
            # Mapping بسيط + تأثير Noosphere
            grid_x = j % 20
            grid_y = (j // 20) % 20
            freq = freq_field[grid_x % freq_field.shape[0], grid_y % freq_field.shape[1]]
            noo_influence = noo_field[grid_x % 20, grid_y % 20]
            
            # Programmable joint position/velocity
            target_pos = freq * 1.8 * (1.0 + 0.5 * awareness) + noo_influence * 0.6
            commands[j] = np.clip(target_pos, -np.pi, np.pi)
        
        return commands

    def _publish_joint_commands(self, commands: np.ndarray):
        """نشر أوامر المفاصل"""
        msg = Float64MultiArray()
        msg.data = commands.tolist()
        self.joint_cmd_pub.publish(msg)
        
        # Trajectory للتحكم الأكثر سلاسة (ros2_control)
        traj = JointTrajectory()
        point = JointTrajectoryPoint()
        point.positions = commands.tolist()
        point.time_from_start.sec = 0
        point.time_from_start.nanosec = 33000000  # ~33ms
        traj.points.append(point)
        self.trajectory_pub.publish(traj)

    def _publish_laser_command(self, awareness: float):
        """نشر أمر ليزر صامت (silent rays)"""
        cmd = {
            "type": "silent_laser_sync",
            "strength": awareness,
            "target_joints": "all",
            "frequency_mod": awareness * 10.0
        }
        msg = String()
        msg.data = str(cmd)
        self.laser_pub.publish(msg)

    def get_bridge_metrics(self) -> Dict:
        """Metrics لـ Prometheus"""
        return {
            "duka_optimus_global_awareness": self.last_coherence,
            "duka_optimus_joint_commands_mean": float(np.mean(self.current_joint_states)),
            "duka_optimus_coherence_impact": self.last_coherence * 100.0
        }


# ─────────────────────────────────────────────────────────────
# Entry Point للتشغيل (Standalone أو داخل pipeline)
# ─────────────────────────────────────────────────────────────
def main(args=None):
    rclpy.init(args=args)
    noosphere = ExpandedNoosphere(num_agents=8, grid_size=16)  # مثال
    bridge = OptimusROS2Bridge(noosphere)
    
    try:
        rclpy.spin(bridge)
    except KeyboardInterrupt:
        pass
    finally:
        bridge.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
