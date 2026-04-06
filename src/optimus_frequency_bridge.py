import pybullet as p
import numpy as np
from src.environment import FrequencyGridWorld

class OptimusFrequencyBridge:
    def __init__(self, urdf_path="optimus_gen2.urdf"):  # أو humanoid.urdf للتجربة
        p.connect(p.GUI)
        self.robot_id = p.loadURDF(urdf_path, [0, 0, 1.0], useFixedBase=False)
        self.num_joints = p.getNumJoints(self.robot_id)
        self.joint_frequency_map = np.zeros((self.num_joints, 3))  # freq, phase, amp
    
    def apply_frequency_field(self, frequency_field: np.ndarray, noosphere_field: np.ndarray):
        """
        ربط حقل الترددات بالروبوت
        """
        for joint in range(self.num_joints):
            # Mapping من الـ grid إلى الـ joint
            grid_x = joint % 12
            grid_y = joint // 12 % 12
            
            freq = frequency_field[grid_x % frequency_field.shape[0], grid_y % frequency_field.shape[1]]
            phase = np.sin(noosphere_field[grid_x % 12, grid_y % 12])  # تأثير الوعي الجماعي
            amp = 1.0 + 0.5 * freq
            
            # Programmable Matter Effect
            target_pos = freq * 1.8 * amp * np.sin(phase + self.joint_frequency_map[joint, 1])
            
            # تطبيق على الـ actuator
            p.setJointMotorControl2(
                self.robot_id, joint,
                p.POSITION_CONTROL,
                targetPosition=target_pos,
                force=abs(freq) * 800,          # قوة حسب السعة
                positionGain=0.8,
                velocityGain=0.6
            )
            
            self.joint_frequency_map[joint] = [freq, phase, amp]
    
    def apply_laser_beam_effect(self, beam):
        """تأثير أشعة الليزر الصامتة على الروبوت"""
        for joint in range(self.num_joints):
            influence = beam["amp"] * np.exp(-0.3 * (joint % 10))
            new_freq = beam["freq"] * influence
            p.setJointMotorControl2(self.robot_id, joint, p.VELOCITY_CONTROL,
                                  targetVelocity=new_freq * 4.0, force=1200)
