"""
Echo Client Example / Echo 客户端示例

Simple echo client using LiteNetLib v0.9.5.2.
使用 LiteNetLib v0.9.5.2 的简单 Echo 客户端。

This client connects to the echo server and sends messages.
此客户端连接到 Echo 服务器并发送消息。
"""

import asyncio
import sys
sys.path.insert(0, '..')

from litenetlib import LiteNetManager, EventBasedNetListener, NetDataReader, ConnectionState


class EchoClientListener(EventBasedNetListener):
    """Event listener for echo client / Echo 客户端的事件监听器"""

    def __init__(self):
        super().__init__()
        self.connected = False

    def on_connection_request(self, request):
        """Server doesn't accept incoming connections / 服务器不接受传入连接"""
        return False

    def on_peer_connected(self, peer):
        """Handle connected to server / 处理已连接到服务器"""
        print(f"[CLIENT] Connected to server: {peer.address}")
        self.connected = True

    def on_peer_disconnect(self, peer, disconnect_reason):
        """Handle disconnect from server / 处理与服务器断开连接"""
        print(f"[CLIENT] Disconnected from server, reason: {disconnect_reason.name}")
        self.connected = False

    def on_network_receive(self, peer, reader: NetDataReader):
        """Handle received data / 处理接收到的数据"""
        data = reader.get_remaining_bytes()
        message = data.decode('utf-8', errors='ignore')
        print(f"[CLIENT] Received from server: {message}")


async def main():
    """Main client function / 客户端主函数"""
    # Create client / 创建客户端
    listener = EchoClientListener()
    client = LiteNetManager(listener)

    # Start client / 启动客户端
    if not client.start(port=0):
        print("[CLIENT] Failed to start")
        return

    print("[CLIENT] Started")

    # Connect to server / 连接到服务器
    host = "127.0.0.1"
    port = 7777

    print(f"[CLIENT] Connecting to {host}:{port}...")
    if not client.connect(host, port):
        print("[CLIENT] Failed to initiate connection")
        client.stop()
        return

    try:
        # Wait for connection / 等待连接
        for _ in range(100):  # 10 seconds timeout
            await client.poll_async()
            if listener.connected:
                break
            await asyncio.sleep(0.1)

        if not listener.connected:
            print("[CLIENT] Connection timeout")
            client.stop()
            return

        # Send some messages / 发送一些消息
        messages = [
            "Hello, LiteNetLib!",
            "This is a test message.",
            "Echo protocol working!",
            "Goodbye!"
        ]

        for msg in messages:
            # Get connected peer / 获取已连接的对等端
            peer = client.get_peer_by_address(host, port)
            if peer and peer.is_connected:
                data = msg.encode('utf-8')
                peer.send(data)
                print(f"[CLIENT] Sent: {msg}")
            await asyncio.sleep(1.0)

        # Wait a bit for responses / 等待响应
        await asyncio.sleep(2.0)

        # Disconnect / 断开连接
        peer = client.get_peer_by_address(host, port)
        if peer:
            peer.disconnect()
            print("[CLIENT] Disconnected")

        # Run network loop a bit more / 运行网络循环一会儿
        for _ in range(50):
            await client.poll_async()
            await asyncio.sleep(0.01)

    except KeyboardInterrupt:
        print("\n[CLIENT] Interrupted")
    finally:
        client.stop()
        print("[CLIENT] Stopped")


if __name__ == "__main__":
    asyncio.run(main())
