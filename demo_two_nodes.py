"""
demo_two_nodes.py — اختبار حقيقي: عقدتان تكتشفان بعضهما وتتراسلان
تشغيل:
    # نافذة 1:
    python demo_two_nodes.py --role alpha --port 8765

    # نافذة 2 (جهاز آخر أو نفس الجهاز):
    python demo_two_nodes.py --role beta --port 8766
"""
import asyncio
import argparse
import logging
import sys
import os

# نضيف المسار
sys.path.insert(0, os.path.dirname(__file__))

from protocol import ĐukaCore, ĐukaMessage, ComponentType
from mesh import ĐukaNet

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(name)s | %(message)s',
    datefmt='%H:%M:%S'
)
logger = logging.getLogger("đuka.demo")


async def run_node(node_id: str, ws_port: int):
    print(f"\n{'='*50}")
    print(f"  🧠 Đuka Node: {node_id}")
    print(f"  🌐 WebSocket Port: {ws_port}")
    print(f"  📡 Discovery: UDP broadcast على منفذ 50000")
    print(f"{'='*50}\n")

    # 1. العقل المركزي
    core = ĐukaCore(node_id=node_id)

    # 2. طبقة الشبكة
    net = ĐukaNet(node_id, config={
        'transport': 'websocket',
        'ws_port': ws_port,
        'simulate_latency': False
    })
    core.register(ComponentType.NET, net)

    # ربط الـ transport callback للرسائل الواردة
    async def on_raw_receive(from_addr: str, data: bytes):
        await net._process_incoming(data, from_addr)

    net.transport.on_receive = on_raw_receive

    # 3. تشغيل WebSocket server
    await net.start_server()
    print(f"✅ [{node_id}] جاهز — أبحث عن عقد أخرى...\n")

    # 4. loop: كل 5 ثوانٍ نرسل رسالة لكل العقد المتصلة
    async def send_loop():
        msg_count = 0
        while True:
            await asyncio.sleep(5)
            stats = net.get_network_stats()
            peers = stats['peers']

            if not peers:
                print(f"[{node_id}] ⏳ لا عقد حتى الآن...")
                continue

            msg_count += 1
            for peer in peers:
                msg = ĐukaMessage(
                    source=node_id,
                    target=peer['id'],
                    component=ComponentType.NET,
                    msg_type='knowledge_share',
                    payload={
                        'msg_id': msg_count,
                        'from': node_id,
                        'data': f"مرحباً من {node_id} — الرسالة #{msg_count}",
                        'genome_hash': hash(node_id + str(msg_count))
                    }
                )
                await net.send(peer['id'], msg)
                print(f"📤 [{node_id}] → [{peer['id']}] رسالة #{msg_count} | latency: {peer['latency_ms']}ms")

    # 5. loop: طباعة إحصائيات كل 10 ثوانٍ
    async def stats_loop():
        while True:
            await asyncio.sleep(10)
            stats = net.get_network_stats()
            print(f"\n📊 [{node_id}] إحصائيات الشبكة:")
            print(f"   عقد متصلة: {len(stats['peers'])}")
            for p in stats['peers']:
                print(f"   • {p['id']} @ {p['address']} | {p['latency_ms']}ms | آخر ظهور: {p['last_seen']}s")
            print()

    # تشغيل كل شيء معاً
    await asyncio.gather(
        core.start(),
        send_loop(),
        stats_loop(),
        return_exceptions=True
    )


async def main():
    parser = argparse.ArgumentParser(description="🚀 Đuka Two-Node Demo")
    parser.add_argument('--role', choices=['alpha', 'beta', 'gamma'], default='alpha')
    parser.add_argument('--port', type=int, default=None)
    args = parser.parse_args()

    ports = {'alpha': 8765, 'beta': 8766, 'gamma': 8767}
    port = args.port or ports[args.role]

    try:
        await run_node(node_id=args.role, ws_port=port)
    except KeyboardInterrupt:
        print(f"\n🛑 [{args.role}] إيقاف...")


if __name__ == "__main__":
    asyncio.run(main())
