# file: duka_mesh.py
import rclpy
from rclpy.node import Node
from transformers import pipeline
import zmq
import threading

# تحميل النموذج اللغوي
nlp = pipeline("text-generation", model="gpt2")

class MeshNode(Node):
    def __init__(self, robot_name, peers):
        super().__init__(f'{robot_name}_mesh_node')
        self.robot_name = robot_name
        self.peers = peers
        self.knowledge = []

        # ROS2 اشتراك بيانات المستشعرات
        self.subscription = self.create_subscription(
            dict,
            f'{robot_name}_sensor_data',
            self.listener_callback,
            10)

        # إعداد ZeroMQ للبث والاستقبال
        context = zmq.Context()
        self.publisher = context.socket(zmq.PUB)
        self.publisher.bind(f"tcp://*:5555")

        self.subscriber = context.socket(zmq.SUB)
        for peer in peers:
            self.subscriber.connect(f"tcp://{peer}:5555")
        self.subscriber.setsockopt_string(zmq.SUBSCRIBE, "")

        # تشغيل Thread للاستقبال
        threading.Thread(target=self.listen_mesh, daemon=True).start()

    def listener_callback(self, data):
        prompt = f"Interpret robot data: {data}"
        interpretation = nlp(prompt, max_length=50)[0]['generated_text']
        self.get_logger().info(f"{self.robot_name} interpretation: {interpretation}")
        self.knowledge.append({"robot": self.robot_name, "text": interpretation})
        # بث التفسير إلى الشبكة
        self.publisher.send_json({"robot": self.robot_name, "text": interpretation})

    def listen_mesh(self):
        while True:
            message = self.subscriber.recv_json()
            if message["robot"] != self.robot_name:  # تجاهل الرسائل الذاتية
                self.knowledge.append(message)
                print(f"{self.robot_name} received from {message['robot']}: {message['text']}")

def main(robot_name="robotA", peers=["127.0.0.1"]):
    rclpy.init()
    node = MeshNode(robot_name, peers)
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == "__main__":
    # مثال تشغيل روبوت A مع نظير واحد
    main("robotA", peers=["192.168.1.20"])
