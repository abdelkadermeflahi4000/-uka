"""
🤖 Đuka Agent - وحدة التعلم المعزز
يدعم PPO مع إمكانية التبادل المعرفي الموزع
"""

from stable_baselines3 import PPO
from stable_baselines3.common.callbacks import BaseCallback, EvalCallback
from stable_baselines3.common.vec_env import DummyVecEnv
import torch
import numpy as np
from typing import Optional, List
import os


class KnowledgeSharingCallback(BaseCallback):
    """
    🔄 Callback لتبادل المعرفة بين الـ Nodes
    يحاكي Virtual Starlink Layer
    """
    
    def __init__(self, node_id: str, peers: List[str], sync_interval: int, verbose: int = 0):
        super().__init__(verbose)
        self.node_id = node_id
        self.peers = peers
        self.sync_interval = sync_interval
        self.knowledge_buffer = []
        
    def _on_step(self) -> bool:
        # جمع الخبرات المحلية
        if self.locals.get("infos"):
            for info in self.locals["infos"]:
                if "knowledge" in info:
                    self.knowledge_buffer.append(info["knowledge"])
        
        # مزامنة دورية مع الـ Peers (محاكاة)
        if self.n_calls % self.sync_interval == 0 and self.peers:
            self._sync_knowledge()
        
        return True
    
    def _sync_knowledge(self):
        """محاكاة تبادل المعرفة مع العقد الأخرى"""
        if not self.knowledge_buffer:
            return
            
        # 📡 إرسال المعرفة (محاكاة)
        avg_knowledge = np.mean(self.knowledge_buffer)
        print(f"🛰️ [{self.node_id}] Sharing knowledge: {avg_knowledge:.2f} → {self.peers}")
        
        # 📥 استقبال معرفة من Peers (محاكاة - هنا نضيف ضوضاء إيجابية)
        received_knowledge = avg_knowledge * np.random.uniform(0.95, 1.05)
        print(f"📥 [{self.node_id}] Received enhanced knowledge: {received_knowledge:.2f}")
        
        # 💡 تطبيق التعلم المستلم (تحسين بسيط في سياسة الوكيل)
        if hasattr(self.model, "policy") and hasattr(self.model.policy, "parameters"):
            # ملاحظة: في تطبيق حقيقي، نستخدم Federated Averaging
            pass
        
        self.knowledge_buffer.clear()


class DukaAgent:
    """
    🧠 وكيل Đuka الرئيسي
    """
    
    def __init__(
        self,
        env,
        config: dict,
        node_id: str = "node_001"
    ):
        self.config = config
        self.node_id = node_id
        
        # 🎯 إعداد الـ Environment
        self.env = DummyVecEnv([lambda: env])
        
        # 🧠 إنشاء نموذج PPO
        self.model = PPO(
            policy=config["agent"]["policy"],
            env=self.env,
            learning_rate=config["agent"]["learning_rate"],
            gamma=config["agent"]["gamma"],
            n_steps=config["agent"]["n_steps"],
            batch_size=config["agent"]["batch_size"],
            n_epochs=config["agent"]["n_epochs"],
            verbose=1,
            tensorboard_log=config["training"]["log_dir"]
        )
        
        # 🔄 Callback لتبادل المعرفة
        self.knowledge_callback = KnowledgeSharingCallback(
            node_id=node_id,
            peers=config["network"]["peers"],
            sync_interval=config["network"]["sync_interval"]
        )
    
    def train(self, total_timesteps: Optional[int] = None):
        """🚀 بدء التدريب"""
        timesteps = total_timesteps or self.config["training"]["total_timesteps"]
        
        print(f"🎯 [{self.node_id}] Starting training for {timesteps} steps...")
        
        self.model.learn(
            total_timesteps=timesteps,
            callback=self.knowledge_callback,
            progress_bar=True
        )
        
        print(f"✅ [{self.node_id}] Training completed!")
        return self.model
    
    def save(self, path: Optional[str] = None):
        """💾 حفظ النموذج"""
        if path is None:
            path = f"{self.config['training']['model_dir']}/{self.node_id}_latest"
        os.makedirs(os.path.dirname(path), exist_ok=True)
        self.model.save(path)
        print(f"💾 Model saved to {path}")
    
    def load(self, path: str):
        """📂 تحميل نموذج محفوظ"""
        self.model = PPO.load(path, env=self.env)
        print(f"📂 Model loaded from {path}")
    
    def predict(self, observation, deterministic: bool = True):
        """🔮 التنبؤ بالإجراء التالي"""
        action, _ = self.model.predict(observation, deterministic=deterministic)
        return action
    
    def get_knowledge_summary(self) -> dict:
        """📊 ملخص المعرفة المكتسبة"""
        return {
            "node_id": self.node_id,
            "model_params": sum(p.numel() for p in self.model.policy.parameters()),
            "training_steps": self.model.num_timesteps,
        }
