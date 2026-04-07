# file: duka_raft.py
import rclpy
from rclpy.node import Node
from transformers import pipeline
import zmq
import threading
import time
import random

nlp = pipeline("text-generation", model="gpt2")

class RaftNode(Node):
    def __init__(self, robot_name, peers):
        super().__init__(f'{robot_name}_raft_node')
        self.robot_name = robot_name
        self.peers = peers
        self.role = "Follower"  # يمكن أن يكون Leader أو Candidate
        self.term = 0
        self.voted_for = None
        self.log = []
        self.leader = None

        # إعداد الشبكة
        context = zmq.Context()
        self.publisher = context.socket(zmq.PUB)
        self.publisher.bind(f"tcp://*:5555")

        self.subscriber = context.socket(zmq.SUB)
        for peer in peers:
            self.subscriber.connect(f"tcp://{peer}:5555")
        self.subscriber.setsockopt_string(zmq.SUBSCRIBE, "")

        threading.Thread(target=self.listen_mesh, daemon=True).start()
        threading.Thread(target=self.election_timer, daemon=True).start()

    def listener_callback(self, data):
        if self.role == "Leader":
            interpretation = nlp(f"Interpret robot data: {data}", max_length=50)[0]['generated_text']
            entry = {"term": self.term, "robot": self.robot_name, "text": interpretation}
            self.log.append(entry)
            self.publisher.send_json({"type": "append_entries", "entry": entry})

    def listen_mesh(self):
        while True:
            message = self.subscriber.recv_json()
            if message["type"] == "request_vote":
                if self.voted_for is None or self.voted_for == message["candidate"]:
                    self.voted_for = message["candidate"]
                    self.publisher.send_json({"type": "vote", "term": message["term"], "voter": self.robot_name})
            elif message["type"] == "vote":
                # إذا حصل المرشح على أغلبية الأصوات يصبح قائد
                pass
            elif message["type"] == "append_entries":
                self.log.append(message["entry"])
                print(f"{self.robot_name} appended entry: {message['entry']}")

    def election_timer(self):
        while True:
            time.sleep(random.randint(5, 10))
            if self.role == "Follower" and self.leader is None:
                self.role = "Candidate"
                self.term += 1
                self.publisher.send_json({"type": "request_vote", "term": self.term, "candidate": self.robot_name})

def main(robot_name="robotA", peers=["127.0.0.1"]):
    rclpy.init()
    node = RaftNode(robot_name, peers)
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == "__main__":
    main("robotA", peers=["192.168.1.20", "192.168.1.21"])
