#!/usr/bin/env python3
"""
🚀 Đuka Protocol - Main Entry Point
Distributed Unified Knowledge Architecture
"""

import asyncio
import argparse
from pathlib import Path
import yaml

from src.environment import DukaGridWorld
from src.agent import DukaAgent
from src.network import ĐukaNetwork, KnowledgePacket


def load_config(config_path: str = "config.yaml") -> dict:
    """📄 تحميل ملف الإعدادات"""
    with open(config_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


async def run_single_node_demo(config: dict):
    """🎯 عرض توضيحي لعقدة واحدة"""
    print("🚀 Starting Đuka Single-Node Demo")
    print("=" * 50)
    
    # 🌍 إنشاء البيئة
    env = DukaGridWorld(
        grid_size=config["environment"]["grid_size"],
        max_steps=config["environment"]["max_steps"],
        render_mode="human" if config["environment"]["render"] else None
    )
    
    # 🤖 إنشاء الوكيل
    agent = DukaAgent(
        env=env,
        config=config,
        node_id=config["network"]["node_id"]
    )
    
    # 🎮 تدريب سريع للعرض
    print("\n🎮 Running quick demo episode...")
    obs, _ = env.reset()
    done = False
    truncated = False
    
    while not (done or truncated):
        if config["environment"]["render"]:
            env.render()
        
        action = agent.predict(obs)
        obs, reward, done, truncated, info = env.step(int(action))
        
        print(f"   Reward: {reward:+.2f} | Knowledge: {info['knowledge']}")
    
    print(f"\n✅ Episode finished! Total knowledge: {info['knowledge']}")
    
    # 💾 حفظ النموذج
    agent.save()
    
    return agent


async def run_network_demo(config: dict):
    """🌐 عرض توضيحي للشبكة الموزعة"""
    print("🛰️ Starting Đuka Network Demo")
    print("=" * 50)
    
    # 🕸️ إنشاء الشبكة
    network = ĐukaNetwork()
    node_ids = ["node_001", "node_002", "node_003"]
    network.create_mesh(node_ids, connectivity=0.8)
    
    # 🔄 تشغيل محاكاة تبادل المعرفة
    await network.run_simulation(duration_steps=5)


def main():
    """🎯 الدالة الرئيسية"""
    parser = argparse.ArgumentParser(description="🚀 Đuka Protocol")
    parser.add_argument("--config", type=str, default="config.yaml", help="مسار ملف الإعدادات")
    parser.add_argument("--mode", type=str, choices=["single", "network", "train"], 
                       default="single", help="وضع التشغيل")
    parser.add_argument("--train", action="store_true", help="تشغيل التدريب الكامل")
    
    args = parser.parse_args()
    config = load_config(args.config)
    
    if args.mode == "single":
        asyncio.run(run_single_node_demo(config))
    
    elif args.mode == "network":
        asyncio.run(run_network_demo(config))
    
    elif args.mode == "train" or args.train:
        print("🎯 Starting Full Training Mode")
        env = DukaGridWorld(
            grid_size=config["environment"]["grid_size"],
            max_steps=config["environment"]["max_steps"]
        )
        agent = DukaAgent(env=env, config=config, node_id=config["network"]["node_id"])
        agent.train()
        agent.save()
        print(f"📊 Knowledge Summary: {agent.get_knowledge_summary()}")


if __name__ == "__main__":
    main()
