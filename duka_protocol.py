# file: duka_protocol.py
import rclpy
from rclpy.node import Node
from transformers import pipeline
from fastapi import FastAPI
import uvicorn
import threading

# 1. تحميل النموذج اللغوي
nlp = pipeline("text-generation", model="gpt2")

# 2. ROS2 Node لاستقبال بيانات المستشعرات
class SensorInterpreter(Node):
    def __init__(self):
        super().__init__('sensor_interpreter')
        self.subscription = self.create_subscription(
            dict,  # بيانات المستشعرات بصيغة JSON
            'sensor_data',
            self.listener_callback,
            10)

    def listener_callback(self, data):
        prompt = f"Interpret robot data: {data}"
        interpretation = nlp(prompt, max_length=50)[0]['generated_text']
        self.get_logger().info(f"Generated interpretation: {interpretation}")
        # إرسال التفسير إلى واجهة المعرفة
        KnowledgeBase.store_interpretation(interpretation)

# 3. واجهة FastAPI لتخزين ومشاركة التفسيرات
app = FastAPI()
class KnowledgeBase:
    interpretations = []

    @classmethod
    def store_interpretation(cls, text):
        cls.interpretations.append(text)

@app.get("/knowledge")
def get_knowledge():
    return {"interpretations": KnowledgeBase.interpretations}

# 4. تشغيل FastAPI في Thread منفصل
def run_api():
    uvicorn.run(app, host="0.0.0.0", port=8000)

# 5. تشغيل النظام بالكامل
def main():
    # تشغيل واجهة الويب
    api_thread = threading.Thread(target=run_api, daemon=True)
    api_thread.start()

    # تشغيل ROS2 Node
    rclpy.init()
    node = SensorInterpreter()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == "__main__":
    main()
