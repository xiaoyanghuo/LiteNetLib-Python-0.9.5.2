"""
LiteNetLib-Python 服务器测试
等待 C# 客户端连接并测试互操作性
"""

import asyncio
import time
from litenetlib import LiteNetManager, EventBasedNetListener
from litenetlib.core.constants import DeliveryMethod, DisconnectReason
from litenetlib.utils.data_writer import NetDataWriter
from litenetlib.utils.data_reader import NetDataReader


class PythonServerTest:
    def __init__(self):
        self.listener = EventBasedNetListener()
        self.manager = None
        client_peer = None
        self.test_results = []
        self._client_peer = None
        self._test_started = False

    async def run(self):
        print("=== LiteNetLib-Python 服务器测试 ===")
        print("等待 C# 客户端连接...\n")

        # 设置事件回调
        self.listener.on_connection_request = self.on_connection_request
        self.listener.on_peer_connected = self.on_peer_connected
        self.listener.on_peer_disconnected = self.on_peer_disconnected
        self.listener.on_network_receive = self.on_network_receive
        self.listener.on_network_receive_unconnected = self.on_network_receive_unconnected

        # 创建管理器
        self.manager = LiteNetManager(self.manager_max_connections, "test_key")
        self.manager.auto_recycle = True
        self.manager.update_time = 15
        self.manager.disconnect_timeout = 5000
        self.manager.use_safe_mtu = True

        # 启动服务器
        if not self.manager.start(9051):
            print("[Python] 服务器启动失败！")
            return

        print("[Python] 服务器已启动，监听端口 9051")
        print("[Python] 按 Ctrl+C 退出...\n")

        # 运行循环
        try:
            while True:
                self.manager.poll()
                await asyncio.sleep(0.015)
        except KeyboardInterrupt:
            print("\n[Python] 收到退出信号")
        finally:
            self.manager.stop()
            self.print_results()

    def manager_max_connections(self, s):
        return 1  # 只接受一个客户端连接

    def on_connection_request(self, request):
        print(f"[Python] 收到连接请求: {request.address}")
        if request.data == b"test_connection":
            request.accept()
        else:
            request.reject()

    def on_peer_connected(self, peer):
        print(f"[Python] ✅ C# 客户端已连接: {peer.address}")
        self._client_peer = peer

        # 延迟发送测试消息
        asyncio.create_task(self.send_test_messages_later(peer))

    def on_peer_disconnected(self, peer, disconnect_info):
        print(f"[Python] 客户端断开: {disconnect_info}")
        self._client_peer = None

    def on_network_receive(self, peer, reader, channel_number, delivery_method):
        try:
            message_type = reader.get_byte()

            if message_type == 1:  # String message
                msg = reader.get_string()
                print(f"[Python] 收到字符串 ({delivery_method.name}): {msg}")
                self.test_results.append(("String message", True))

            elif message_type == 2:  # Integer array
                count = reader.get_int()
                numbers = [reader.get_int() for _ in range(count)]
                print(f"[Python] 收到整数数组 ({count} 个): {numbers}")
                self.test_results.append(("Integer array", True))

            elif message_type == 3:  # Large data
                size = reader.get_int()
                data = reader.get_bytes_with_length()
                print(f"[Python] 收到大块数据: {len(data)} 字节 (预期 {size} 字节)")
                self.test_results.append(("Large data", len(data) == size))

            elif message_type == 10:  # Test start signal
                print("[Python] 收到测试开始信号")
                asyncio.create_task(self.send_test_messages(peer))

        except Exception as e:
            print(f"[Python] 处理消息错误: {e}")
            import traceback
            traceback.print_exc()

    def on_network_receive_unconnected(self, address, reader, message_type):
        print(f"[Python] 收到非连接消息")

    async def send_test_messages_later(self, peer):
        await asyncio.sleep(0.5)
        await self.send_test_messages(peer)

    async def send_test_messages(self, peer):
        if self._test_started:
            return
        self._test_started = True

        await asyncio.sleep(0.5)

        print("\n[Python] === 开始发送测试消息到 C# 客户端 ===\n")

        # 1. Unreliable 消息
        writer = NetDataWriter()
        writer.put_byte(1)
        writer.put_string("Hello from Python Server!")
        peer.send(writer, DeliveryMethod.UNRELIABLE)
        print("[Python] 发送: Unreliable 字符串消息")

        await asyncio.sleep(0.1)

        # 2. ReliableOrdered 消息
        writer = NetDataWriter()
        writer.put_byte(1)
        writer.put_string("Python 服务器消息 - 测试中文！")
        peer.send(writer, DeliveryMethod.RELIABLE_ORDERED)
        print("[Python] 发送: ReliableOrdered UTF-8 字符串")

        await asyncio.sleep(0.1)

        # 3. 整数数组
        writer = NetDataWriter()
        writer.put_byte(2)
        writer.put_int(5)  # Count
        for i in range(1, 6):
            writer.put_int(i * 1000)
        peer.send(writer, DeliveryMethod.RELIABLE_UNORDERED)
        print("[Python] 发送: ReliableUnordered 整数数组")

        await asyncio.sleep(0.1)

        # 4. Sequenced 消息
        for i in range(1, 4):
            writer = NetDataWriter()
            writer.put_byte(1)
            writer.put_string(f"Sequenced msg {i}")
            peer.send(writer, DeliveryMethod.SEQUENCED)
        print("[Python] 发送: 3 个 Sequenced 消息")

        await asyncio.sleep(0.1)

        # 5. ReliableSequenced 消息
        for i in range(1, 4):
            writer = NetDataWriter()
            writer.put_byte(1)
            writer.put_string(f"ReliableSequenced msg {i}")
            peer.send(writer, DeliveryMethod.RELIABLE_SEQUENCED)
        print("[Python] 发送: 3 个 ReliableSequenced 消息")

        print("\n[Python] === 测试消息发送完成 ===\n")

    def print_results(self):
        print("\n" + "="*60)
        print("Python 服务器测试结果:")
        print("="*60)

        if self.test_results:
            for test_name, passed in self.test_results:
                status = "✅ 通过" if passed else "❌ 失败"
                print(f"{status} - {test_name}")
        else:
            print("没有收到测试结果")

        print("="*60)


async def main():
    test = PythonServerTest()
    await test.run()


if __name__ == "__main__":
    asyncio.run(main())
