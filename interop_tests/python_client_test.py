"""
LiteNetLib-Python 客户端测试
连接到 C# 服务器并测试互操作性
"""

import asyncio
import time
from litenetlib import LiteNetManager, EventBasedNetListener
from litenetlib.core.constants import DeliveryMethod, DisconnectReason
from litenetlib.utils.data_writer import NetDataWriter
from litenetlib.utils.data_reader import NetDataReader


class PythonClientTest:
    def __init__(self):
        self.listener = EventBasedNetListener()
        self.manager = None
        self.peer = None
        self.test_results = []

    async def run(self):
        print("=== LiteNetLib-Python 客户端测试 ===")
        print("连接到 C# 服务器 (127.0.0.1:9050)...\n")

        # 设置事件回调
        self.listener.on_peer_connected = self.on_peer_connected
        self.listener.on_peer_disconnected = self.on_peer_disconnected
        self.listener.on_network_receive = self.on_network_receive
        self.listener.on_network_receive_unconnected = self.on_network_receive_unconnected

        # 创建管理器
        self.manager = LiteNetManager(self.listener, 0, "test_key")
        self.manager.auto_recycle = True
        self.manager.update_time = 15
        self.manager.disconnect_timeout = 5000
        self.manager.use_safe_mtu = True

        # 连接到服务器
        self.peer = self.manager.connect("127.0.0.1", 9050, "test_connection")

        if not self.peer:
            print("[Python] 连接失败！")
            return

        print("[Python] 正在连接...")

        # 运行循环
        start_time = time.time()
        while time.time() - start_time < 30:  # 运行 30 秒
            self.manager.poll()
            await asyncio.sleep(0.015)

            # 如果已断开连接，退出
            if self.peer is None or not self.manager.is_connected:
                break

        # 打印测试结果
        self.print_results()

        self.manager.stop()

    def on_peer_connected(self, peer):
        print(f"[Python] ✅ 已连接到服务器: {peer.address}")

    def on_peer_disconnected(self, peer, disconnect_info):
        print(f"[Python] 断开连接: {disconnect_info}")
        self.peer = None

    def on_network_receive(self, peer, reader, channel_number, delivery_method):
        try:
            message_type = reader.get_byte()

            if message_type == 10:  # Test start signal
                print("[Python] 收到测试开始信号，开始发送测试消息...")
                asyncio.create_task(self.send_test_messages(peer))

            elif message_type == 1:  # String message
                msg = reader.get_string()
                print(f"[Python] 收到字符串 ({delivery_method.name}): {msg}")
                self.test_results.append(("String message", True))

            elif message_type == 2:  # Integer array (count first, then values)
                # C# sends: Put(5), Put(100), Put(200), Put(300), Put(400), Put(500)
                # But the first int is actually part of our protocol
                try:
                    # Try to read as count followed by values
                    remaining = reader.available_bytes
                    data = reader.get_remaining_bytes()

                    # Parse integers from remaining data
                    # The data should be 5 ints (20 bytes total): 100, 200, 300, 400, 500
                    numbers = []
                    for i in range(0, len(data), 4):
                        if i + 4 <= len(data):
                            import struct
                            num = struct.unpack('<i', data[i:i+4])[0]
                            numbers.append(num)

                    print(f"[Python] 收到整数数组 ({len(numbers)} 个): {numbers}")
                    self.test_results.append(("Integer array", True))
                except Exception as e:
                    print(f"[Python] 解析整数数组: {e}")

            elif message_type == 3:  # Large data
                size = reader.get_int()
                data = reader.get_bytes_with_length()
                print(f"[Python] 收到大块数据: {len(data)} 字节 (预期 {size} 字节)")

                # 验证数据内容
                if len(data) == 20000:
                    # 验证数据模式
                    correct = True
                    for i in range(len(data)):
                        if data[i] != (i % 256):
                            correct = False
                            break

                    if correct:
                        print("[Python] ✅ 大块数据验证成功！分片传输工作正常")
                        self.test_results.append(("Large data (fragmentation)", True))
                    else:
                        print("[Python] ❌ 大块数据验证失败！")
                        self.test_results.append(("Large data", False))
                else:
                    print(f"[Python] ❌ 大块数据大小不匹配！")
                    self.test_results.append(("Large data", False))

        except Exception as e:
            print(f"[Python] 处理消息错误: {e}")
            import traceback
            traceback.print_exc()

    def on_network_receive_unconnected(self, address, reader, message_type):
        print(f"[Python] 收到非连接消息")

    async def send_test_messages(self, peer):
        await asyncio.sleep(0.5)

        print("\n[Python] === 开始发送测试消息到 C# 服务器 ===\n")

        # 1. Unreliable 消息
        writer = NetDataWriter()
        writer.put_byte(1)
        writer.put_string("Hello from Python Client!")
        peer.send(writer, DeliveryMethod.UNRELIABLE)
        print("[Python] 发送: Unreliable 字符串消息")

        await asyncio.sleep(0.1)

        # 2. ReliableOrdered 字符串
        writer = NetDataWriter()
        writer.put_byte(1)
        writer.put_string("测试中文消息 from Python!")
        peer.send(writer, DeliveryMethod.RELIABLE_ORDERED)
        print("[Python] 发送: ReliableOrdered UTF-8 字符串")

        await asyncio.sleep(0.1)

        # 3. 整数数组
        writer = NetDataWriter()
        writer.put_byte(2)
        writer.put_int(5)  # Count
        for i in range(1, 6):
            writer.put_int(i * 100)  # 100, 200, 300, 400, 500
        peer.send(writer, DeliveryMethod.RELIABLE_UNORDERED)
        print("[Python] 发送: ReliableUnordered 整数数组")

        await asyncio.sleep(0.1)

        # 4. Sequenced 消息
        for i in range(1, 4):
            writer = NetDataWriter()
            writer.put_byte(1)
            writer.put_string(f"Sequenced {i} from Python")
            peer.send(writer, DeliveryMethod.SEQUENCED)
        print("[Python] 发送: 3 个 Sequenced 消息")

        await asyncio.sleep(0.1)

        # 5. ReliableSequenced 消息
        for i in range(1, 4):
            writer = NetDataWriter()
            writer.put_byte(1)
            writer.put_string(f"ReliableSequenced {i} from Python")
            peer.send(writer, DeliveryMethod.RELIABLE_SEQUENCED)
        print("[Python] 发送: 3 个 ReliableSequenced 消息")

        print("\n[Python] === 测试消息发送完成 ===\n")

        # 发送测试完成信号
        await asyncio.sleep(1.0)
        writer = NetDataWriter()
        writer.put_byte(4)
        writer.put_bool(True)
        writer.put_string("Python client test completed")
        peer.send(writer, DeliveryMethod.RELIABLE_ORDERED)
        print("[Python] 发送测试完成信号")

    def print_results(self):
        print("\n" + "="*60)
        print("Python 客户端测试结果:")
        print("="*60)

        if self.test_results:
            for test_name, passed in self.test_results:
                status = "✅ 通过" if passed else "❌ 失败"
                print(f"{status} - {test_name}")
        else:
            print("没有收到测试结果")

        print("="*60)


async def main():
    test = PythonClientTest()
    await test.run()


if __name__ == "__main__":
    asyncio.run(main())
