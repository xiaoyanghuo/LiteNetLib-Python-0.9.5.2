"""
Echo Server Example / Echo 服务器示例

Simple echo server using LiteNetLib v0.9.5.2.
使用 LiteNetLib v0.9.5.2 的简单 Echo 服务器。

This server listens for connections and echoes back any data received.
此服务器监听连接并回显接收到的任何数据。
"""

import asyncio
import sys
sys.path.insert(0, '..')

from litenetlib import LiteNetManager, EventBasedNetListener, NetDataReader


class EchoServerListener(EventBasedNetListener):
    """Event listener for echo server / Echo 服务器的事件监听器"""

    def __init__(self):
        super().__init__()
        self.peers = set()

    def on_connection_request(self, request):
        """Handle connection request / 处理连接请求"""
        print(f"[SERVER] Connection request from {request.address}")
        return True  # Accept all connections / 接受所有连接

    def on_peer_connected(self, peer):
        """Handle peer connected / 处理对等端已连接"""
        print(f"[SERVER] Peer connected: {peer.address}")
        self.peers.add(peer)

    def on_peer_disconnect(self, peer, disconnect_reason):
        """Handle peer disconnect / 处理对等端断开连接"""
        print(f"[SERVER] Peer disconnected: {peer.address}, reason: {disconnect_reason.name}")
        if peer in self.peers:
            self.peers.remove(peer)

    def on_network_receive(self, peer, reader: NetDataReader):
        """Handle received data / 处理接收到的数据"""
        data = reader.get_remaining_bytes()
        message = data.decode('utf-8', errors='ignore')
        print(f"[SERVER] Received from {peer.address}: {message}")

        # Echo back / 回显
        peer.send(data)
        print(f"[SERVER] Echoed to {peer.address}")


async def main():
    """Main server function / 服务器主函数"""
    # Create server / 创建服务器
    listener = EchoServerListener()
    server = LiteNetManager(listener)

    # Start server on port 7777 / 在端口 7777 启动服务器
    port = 7777
    if not server.start(port=port):
        print(f"[SERVER] Failed to start on port {port}")
        return

    print(f"[SERVER] Started on port {server.local_port}")
    print("[SERVER] Press Ctrl+C to stop")

    try:
        # Run network loop / 运行网络循环
        while server.is_running:
            await server.poll_async()
            await asyncio.sleep(0.001)
    except KeyboardInterrupt:
        print("\n[SERVER] Shutting down...")
    finally:
        server.stop()
        print("[SERVER] Stopped")


if __name__ == "__main__":
    asyncio.run(main())
