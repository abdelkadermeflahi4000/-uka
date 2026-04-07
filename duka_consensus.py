# file: duka_consensus.py
import rclpy
from rclpy.node import Node
from transformers import pipeline
import zmq
import threading
import uuid

# تحميل النموذج اللغوي
nlp = pipeline("text-generation", model="gpt2")

class ConsensusNode(Node):
    def __init__(self, robot_name, peers):
        super().__init__(f'{robot_name}_consensus_node')
        self.robot_name = robot_name
        self.peers = peers
        self.knowledge = []
        self.votes = {}

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
        msg_id = str(uuid.uuid4())
        message = {"id": msg_id, "robot": self.robot_name, "text": interpretation, "type": "proposal"}
        self.publisher.send_json(message)
        self.votes[msg_id] = {self.robot_name: True}  # الروبوت يصوت لنفسه

    def listen_mesh(self):
        while True:
            message = self.subscriber.recv_json()
            msg_id = message["id"]

            if message["type"] == "proposal":
                # التصويت على الاقتراح
                vote = {"id": msg_id, "robot": self.robot_name, "vote": True, "type": "vote"}
                self.publisher.send_json(vote)

            elif message["type"] == "vote":
                if msg_id not in self.votes:
                    self.votes[msg_id] = {}
                self.votes[msg_id][message["robot"]] = message["vote"]

                # تحقق من الأغلبية
                if len(self.votes[msg_id]) >= (len(self.peers) + 1) // 2 + 1:
                    # اعتماد التفسير
                    for proposal in self.knowledge:
                        if proposal["id"] == msg_id:
                            return
                    self.knowledge.append({"id": msg_id, "text": message.get("text", ""), "robot": message["robot"]})
                    print(f"{self.robot_name} consensus reached for {msg_id}")

def main(robot_name="robotA", peers=["127.0.0.1"]):
    rclpy.init()
    node = ConsensusNode(robot_name, peers)
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == "__main__":
    main("robotA", peers=["192.168.1.20", "192.168.1.21"])
