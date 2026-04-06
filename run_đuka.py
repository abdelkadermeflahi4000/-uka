#!/usr/bin/env python3
"""
🧠 Đuka Protocol — Unified Launcher
تشغيل أي تركيبة من الوحدات الخمس

مثال:
    python run_đuka.py --node-id alpha --enable-net --enable-bio
"""

import asyncio
import argparse

# ✅ FIX COMPLETE: استبدال كل الـ imports الوهمية بالملفات الحقيقية
#
#   قبل (خاطئ):              بعد (صحيح):
#   from đuka_core import … → from protocol import …
#   from đuka_net import …  → from mesh import …
#   from đuka_sim import …  → from environment import …
#   from đuka_bio import …  → from ethics import …
#   from đuka_robotics import → from ros2_bridge import …

from protocol import ĐukaCore, ComponentType
from mesh import ĐukaNet
from environment import SimulationEnvironment
from ethics import ĐukaBio
from ros2_bridge import ROS2Bridge, RoboticsExecutor


async def main():
    parser = argparse.ArgumentParser(description="🚀 Đuka Protocol Launcher")
    parser.add_argument('--node-id', required=True, help="معرف العقدة الفريد")
    parser.add_argument('--enable-net',      action='store_true', help="تفعيل طبقة الشبكة")
    parser.add_argument('--enable-sim',      action='store_true', help="تفعيل المحاكاة")
    parser.add_argument('--enable-bio',      action='store_true', help="تفعيل وحدة الأخلاقيات")
    parser.add_argument('--enable-robotics', action='store_true', help="تفعيل تكامل الروبوتات")
    parser.add_argument('--config',          default='config.yaml', help="ملف الإعدادات")

    args = parser.parse_args()

    # 1️⃣ إنشاء العقل المركزي
    core = ĐukaCore(node_id=args.node_id)

    bio = None  # نحتاجه في robotics أيضاً

    # 2️⃣ تفعيل الوحدات المطلوبة
    if args.enable_bio:
        bio = ĐukaBio(args.node_id)
        core.register(ComponentType.BIO, bio)

    if args.enable_net:
        net = ĐukaNet(args.node_id, config={'transport': 'simulation', 'simulate_latency': True})
        core.register(ComponentType.NET, net)

    if args.enable_sim:
        sim = SimulationEnvironment(
            env_id=f"{args.node_id}_sim",
            config={'time_scale': 100, 'sync_with_network': args.enable_net}
        )
        core.register(ComponentType.SIM, sim)

    if args.enable_robotics:
        executor = RoboticsExecutor(robot_id=args.node_id, bio_module=bio)
        # ROS2Bridge يُضاف فقط إذا كان ROS2 متاحاً
        try:
            import rclpy
            rclpy.init()
            ros_bridge = ROS2Bridge(f"{args.node_id}_ros", core)
            executor.ros_bridge = ros_bridge
            print("✅ ROS2 Bridge متصل")
        except ImportError:
            print("⚠️ ROS2 غير مُثبت — executor في وضع محاكاة")
        core.register(ComponentType.ROBOTICS, executor)

    # 3️⃣ بدء التشغيل
    print(f"\n🧠 Starting Đuka Node: {args.node_id}")
    print(f"📦 Active components: {[c.name for c in core.components.keys()]}")

    try:
        await core.start()
    except KeyboardInterrupt:
        print("\n🛑 Shutting down gracefully...")
        core.stop()
        try:
            import rclpy
            rclpy.shutdown()
        except Exception:
            pass


if __name__ == "__main__":
    asyncio.run(main())
