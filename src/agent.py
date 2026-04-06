import numpy as np
import torch as th
from stable_baselines3 import PPO
from stable_baselines3.common.torch_layers import BaseFeaturesExtractor
from typing import Dict, Tuple
import gymnasium as gym

class LaserGeneticAgent:
    """
    LaserGeneticAgent - Đuka Protocol Phase 1
    - يجمع بين Reinforcement Learning (PPO) + Genetic Encoding
    - يتعلم يبرمج أشعة الليزر والأشعة الصامتة بنفسه
    - يحاول الوصول إلى Perfect Reality Match (الواقع يبدو طبيعي 100%)
    """
    
    def __init__(self, env: gym.Env, device: str = "auto"):
        self.env = env
        self.device = device
        
        # ==================== Genetic Encoding ====================
        self.genome_size = 64
        self.genome = np.random.uniform(-1.0, 1.0, self.genome_size)
        
        # جينات مهمة:
        # 0-7   : حساسية الترددات
        # 8-15  : قوة برمجة الزمن
        # 16-23 : تفضيل الأشعة الصامتة
        # 24-31 : كفاءة Reality Match
        # 32-63 : معلمات الـ PPO المعدلة
        self.genome[0:8] = 0.85      # حساسية عالية للتردد
        self.genome[8:16] = 0.75     # برمجة زمن قوية
        self.genome[16:24] = 0.9     # تفضيل الأشعة الصامتة
        self.genome[24:32] = 0.95    # هدف Reality Match
        
        # ==================== PPO Model ====================
        policy_kwargs = dict(
            net_arch=[256, 256, 128],
            activation_fn=th.nn.ReLU,
            features_extractor_class=CustomFeatureExtractor,
            features_extractor_kwargs={"genome": self.genome}
        )
        
        self.model = PPO(
            "MlpPolicy",
            env,
            verbose=1,
            device=self.device,
            learning_rate=3e-4,
            n_steps=2048,
            batch_size=512,
            gamma=0.99,
            tensorboard_log="./tensorboard/đuka_laser/",
            policy_kwargs=policy_kwargs
        )
    
    def get_laser_action(self, obs: np.ndarray) -> Dict:
        """يقرر إطلاق ليزر جديد حسب الـ genome"""
        freq_base = np.tanh(self.genome[0:8].mean()) * 0.9 + 0.1
        is_silent = np.random.rand() < self.genome[16:24].mean()
        
        # اختيار اتجاه ذكي
        directions = [(1,0), (-1,0), (0,1), (0,-1), (1,1), (-1,1), (1,-1), (-1,-1)]
        dir_idx = int(np.abs(self.genome[8:16]).argmax() % 8)
        
        return {
            "start": tuple(self.env.agent_pos),
            "direction": directions[dir_idx],
            "frequency": float(freq_base + 0.1 * self.genome[24]),
            "amplitude": 1.0,
            "is_silent": bool(is_silent),
            "duration": int(6 + 4 * abs(self.genome[8]))
        }
    
    def learn(self, total_timesteps: int = 50000):
        """التدريب مع تطور الـ genome"""
        print("🚀 بدء تدريب LaserGeneticAgent...")
        
        for iteration in range(0, total_timesteps, 10000):
            self.model.learn(total_timesteps=10000, reset_num_timesteps=False)
            
            # Evolution: Mutation + Selection
            if iteration % 20000 == 0 and iteration > 0:
                self.evolve_genome()
                print(f"🧬 Evolution at step {iteration} | Reality Match Goal: {self.genome[24:32].mean():.3f}")
        
        self.model.save("models/duka_laser_genetic_agent")
        print("✅ التدريب انتهى - النموذج محفوظ")
    
    def evolve_genome(self):
        """تطور الجينوم (Mutation + Crossover)"""
        # Mutation
        mutation = np.random.normal(0, 0.15, self.genome_size)
        self.genome += mutation * (1 - abs(self.genome))
        
        # Clamp
        self.genome = np.clip(self.genome, -1.0, 1.0)
        
        # Reward good genes (Reality Match)
        self.genome[24:32] = np.clip(self.genome[24:32] + 0.08, 0.7, 1.0)
    
    def predict(self, obs: np.ndarray, deterministic: bool = False):
        action, _ = self.model.predict(obs, deterministic=deterministic)
        return action
    
    def save(self, path: str):
        self.model.save(path)
        np.save(f"{path}_genome.npy", self.genome)
    
    def load(self, path: str):
        self.model = PPO.load(path, env=self.env)
        self.genome = np.load(f"{path}_genome.npy")


# ==================== Feature Extractor (يدمج الـ genome) ====================
class CustomFeatureExtractor(BaseFeaturesExtractor):
    def __init__(self, observation_space: gym.spaces.Box, genome: np.ndarray):
        super().__init__(observation_space, features_dim=256)
        self.genome = th.tensor(genome, dtype=th.float32)
    
    def forward(self, observations: th.Tensor) -> th.Tensor:
        # Flatten grid + inject genome
        flat = observations.view(observations.shape[0], -1)
        genome_expanded = self.genome.unsqueeze(0).expand(flat.shape[0], -1)
        combined = th.cat([flat, genome_expanded], dim=1)
        return combined
