# file: duka_network.py
import rclpy
from rclpy.node import Node
from transformers import pipeline
from fastapi import FastAPI
import uvicorn
import threading
import requests

# تحميل النموذج اللغوي
nlp = pipeline("text-generation", model="gpt2")

# قاعدة المعرفة المشتركة
class KnowledgeBase:
    interpretations = []

    @classmethod
    def store(cls, text, source_robot):
        cls.interpretations.append({"robot": source_robot, "text": text})

    @classmethod
    def get_all(cls):
        return cls.interpretations

# واجهة FastAPI لتبادل المعرفة
app = FastAPI()

@app.get("/knowledge")
def get_knowledge():
    return {"interpretations": KnowledgeBase.get_all()}

# عقدة ROS2 لتفسير البيانات
class SensorInterpreter(Node):
    def __init__(self, robot_name):
        super().__init__(f'{robot_name}_interpreter')
        self.robot_name = robot_name
        self.subscription = self.create_subscription(
            dict,  # بيانات المستشعرات بصيغة JSON
            f'{robot_name}_sensor_data',
            self.listener_callback,
            10)

    def listener_callback(self, data):
        prompt = f"Interpret robot data: {data}"
        interpretation = nlp(prompt, max_length=50)[0]['generated_text']
        self.get_logger().info(f"{self.robot_name} interpretation: {interpretation}")
        # تخزين التفسير في الشبكة
        KnowledgeBase.store(interpretation, self.robot_name)

# تشغيل واجهة الويب في Thread منفصل
def run_api():
    uvicorn.run(app, host="0.0.0.0", port=8000)

# تشغيل النظام
def main(robot_name="robotA"):
    api_thread = threading.Thread(target=run_api, daemon=True)
    api_thread.start()

    rclpy.init()
    node = SensorInterpreter(robot_name)
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == "__main__":
    main("robotA")
