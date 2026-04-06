#!/usr/bin/env python3
"""
🧠 Đuka Protocol — Unified Launcher
تشغيل أي تركيبة من الوحدات الخمس
"""

import asyncio
import argparse
from đuka_core import ĐukaCore, ComponentType
from đuka_net import ĐukaNet
from đuka_sim import SimulationEnvironment
from đuka_bio import ĐukaBio
from đuka_robotics import ROS2Bridge, RoboticsExecutor

async def main():
    parser = argparse.ArgumentParser(description="🚀 Đuka Protocol Launcher")
    parser.add_argument('--node-id', required=True, help="معرف العقدة الفريد")
    parser.add_argument('--enable-net', action='store_true', help="تفعيل طبقة الشبكة")
    parser.add_argument('--enable-sim', action='store_true', help="تفعيل المحاكاة")
    parser.add_argument('--enable-bio', action='store_true', help="تفعيل وحدة الأخلاقيات")
    parser.add_argument('--enable-robotics', action='store_true', help="تفعيل تكامل الروبوتات")
    parser.add_argument('--config', default='config.yaml', help="ملف الإعدادات")
    
    args = parser.parse_args()
    
    # 1️⃣ إنشاء العقل المركزي
    core = ĐukaCore(node_id=args.node_id)
    
    # 2️⃣ تفعيل الوحدات المطلوبة
    if args.enable_net:
        net = ĐukaNet(args.node_id, config={'simulate_latency': True})
        core.register(ComponentType.NET, net)
        
    if args.enable_sim:
        sim = SimulationEnvironment(env_id=f"{args.node_id}_sim", config={'time_scale': 100})
        core.register(ComponentType.SIM, sim)
        
    if args.enable_bio:
        bio = ĐukaBio(args.node_id)
        core.register(ComponentType.BIO, bio)
        
    if args.enable_robotics:
        # يحتاج ROS2 مُهيأ مسبقاً
        rclpy.init()
        ros_bridge = ROS2Bridge(f"{args.node_id}_ros", core)
        executor = RoboticsExecutor(args.node_id, bio if args.enable_bio else None)
        executor.ros_bridge = ros_bridge
        core.register(ComponentType.ROBOTICS, executor)
    
    # 3️⃣ بدء التشغيل
    print(f"🧠 Starting Đuka Node: {args.node_id}")
    print(f"📦 Active components: {[c.name for c in core.components.keys()]}")
    
    try:
        await core.start()
    except KeyboardInterrupt:
        print("\n🛑 Shutting down...")
        core.stop()
        if args.enable_robotics:
            rclpy.shutdown()

if __name__ == "__main__":
    asyncio.run(main())
