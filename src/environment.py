"""
🌍 Đuka Environment - GridWorld Simulation
بيئة شبكة ذكية يتعلم فيها الوكيل التنقل وجمع المعرفة
"""

import gymnasium as gym
import numpy as np
from gymnasium import spaces
from typing import Dict, Optional, Tuple


class DukaGridWorld(gym.Env):
    """
    بيئة GridWorld لـ Đuka:
    - شبكة ثنائية الأبعاد
    - أهداف (معرفة) للعناصر الإيجابية
    - عقبات للعناصر السلبية
    - وكيل يتعلم التنقل الأمثل
    """
    
    metadata = {"render_modes": ["human", "rgb_array"], "render_fps": 4}
    
    def __init__(
        self,
        grid_size: int = 10,
        max_steps: int = 100,
        n_goals: int = 3,
        n_obstacles: int = 5,
        render_mode: Optional[str] = None,
    ):
        super().__init__()
        
        self.grid_size = grid_size
        self.max_steps = max_steps
        self.n_goals = n_goals
        self.n_obstacles = n_obstacles
        self.render_mode = render_mode
        
        # 🎮 مساحة الأفعال: [أعلى، أسفل، يسار، يمين، بقاء]
        self.action_space = spaces.Discrete(5)
        
        # 👁️ مساحة الملاحظة: [موقع الوكيل، مواقع الأهداف، مواقع العقبات]
        self.observation_space = spaces.Box(
            low=0, high=grid_size - 1, shape=(3, 2), dtype=np.int32
        )
        
        # 📊 متتبع المعرفة المكتسبة
        self.knowledge_collected = 0
        
        self._reset_environment()
    
    def _reset_environment(self):
        """إعادة تهيئة البيئة عشوائياً"""
        # موقع الوكيل
        self.agent_pos = np.array([
            np.random.randint(0, self.grid_size),
            np.random.randint(0, self.grid_size)
        ])
        
        # توليد الأهداف (معرفة إيجابية)
        self.goals = self._generate_unique_positions(self.n_goals, exclude=[self.agent_pos.tolist()])
        
        # توليد العقبات (تحديات)
        self.obstacles = self._generate_unique_positions(
            self.n_obstacles, 
            exclude=[self.agent_pos.tolist()] + self.goals.tolist()
        )
        
        self.current_step = 0
        self.knowledge_collected = 0
    
    def _generate_unique_positions(self, n: int, exclude: list) -> np.ndarray:
        """توليد مواقع فريدة غير متداخلة"""
        positions = []
        while len(positions) < n:
            pos = [np.random.randint(0, self.grid_size), np.random.randint(0, self.grid_size)]
            if pos not in exclude and pos not in positions:
                positions.append(pos)
        return np.array(positions)
    
    def reset(self, seed: Optional[int] = None, options: Optional[Dict] = None) -> Tuple[np.ndarray, Dict]:
        super().reset(seed=seed)
        self._reset_environment()
        return self._get_observation(), {"knowledge": self.knowledge_collected}
    
    def _get_observation(self) -> np.ndarray:
        """جمع حالة البيئة الحالية"""
        return np.array([
            self.agent_pos,
            self.goals[0] if len(self.goals) > 0 else [0, 0],  # أقرب هدف
            self.obstacles[0] if len(self.obstacles) > 0 else [0, 0]  # أقرب عقبة
        ], dtype=np.int32)
    
    def step(self, action: int) -> Tuple[np.ndarray, float, bool, bool, Dict]:
        """
        تنفيذ خطوة في البيئة
        Returns: observation, reward, terminated, truncated, info
        """
        self.current_step += 1
        
        # 🎮 تحريك الوكيل
        old_pos = self.agent_pos.copy()
        if action == 0:  # أعلى
            self.agent_pos[0] = max(0, self.agent_pos[0] - 1)
        elif action == 1:  # أسفل
            self.agent_pos[0] = min(self.grid_size - 1, self.agent_pos[0] + 1)
        elif action == 2:  # يسار
            self.agent_pos[1] = max(0, self.agent_pos[1] - 1)
        elif action == 3:  # يمين
            self.agent_pos[1] = min(self.grid_size - 1, self.agent_pos[1] + 1)
        # action == 4: بقاء في المكان
        
        # 🎯 حساب المكافأة
        reward = -0.01  # عقوبة زمنية طفيفة لتشجيع الكفاءة
        
        # مكافأة جمع المعرفة (الوصول لهدف)
        for i, goal in enumerate(self.goals):
            if np.array_equal(self.agent_pos, goal):
                reward += 1.0
                self.knowledge_collected += 1
                self.goals = np.delete(self.goals, i, axis=0)  # إزالة الهدف المجمّع
                break
        
        # عقوبة الاصطدام
        for obstacle in self.obstacles:
            if np.array_equal(self.agent_pos, obstacle):
                reward -= 0.5
                self.agent_pos = old_pos  # التراجع
                break
        
        # 🏁 شروط النهاية
        terminated = len(self.goals) == 0  # جمع كل المعرفة
        truncated = self.current_step >= self.max_steps
        
        info = {
            "knowledge": self.knowledge_collected,
            "remaining_goals": len(self.goals),
            "position": self.agent_pos.copy()
        }
        
        return self._get_observation(), reward, terminated, truncated, info
    
    def render(self):
        """عرض البيئة بصرياً"""
        if self.render_mode == "human":
            grid = np.full((self.grid_size, self.grid_size), "·")
            
            # رسم العقبات
            for obs in self.obstacles:
                grid[obs[0], obs[1]] = "█"
            
            # رسم الأهداف
            for goal in self.goals:
                grid[goal[0], goal[1]] = "★"
            
            # رسم الوكيل
            grid[self.agent_pos[0], self.agent_pos[1]] = "●"
            
            print(f"\n🧠 Đuka GridWorld | خطوة: {self.current_step} | معرفة: {self.knowledge_collected}")
            print("   " + " ".join(str(i) for i in range(self.grid_size)))
            for i, row in enumerate(grid):
                print(f"{i:2d} " + " ".join(row))
            print()
