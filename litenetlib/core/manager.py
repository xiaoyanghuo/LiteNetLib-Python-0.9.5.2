"""
Network manager for LiteNetLib v0.9.5.2 / LiteNetLib v0.9.5.2 网络管理器

Main class for all network operations. Can be used as client and/or server.
所有网络操作的主类。可以用作客户端和/或服务器。

Ported from: LiteNetLib/NetManager.cs (v0.9.5.2)
"""

import asyncio
import socket
import time
from typing import Dict, Optional, Set, Callable, Any
from litenetlib.core.constants import NetConstants, PacketProperty, DisconnectReason
from litenetlib.core.packet import NetPacket, NetPacketPool
from litenetlib.core.peer import NetPeer
from litenetlib.core.events import EventBasedNetListener, INetEventListener
from litenetlib.core.connection_request import ConnectionRequest
from litenetlib.utils.net_utils import NetUtils


class LiteNetManager:
    """
    Main network manager class / 主网络管理器类

    Manages socket, peers, and network events.
    管理 socket、对等端和网络事件。

    C# Reference: NetManager
    """

    def __init__(self, listener: Optional[INetEventListener] = None):
        """
        Create network manager / 创建网络管理器。

        Args:
            listener: Event listener for network events / 网络事件监听器
        """
        self._listener = listener
        self._peers: Dict[tuple, NetPeer] = {}
        self._socket: Optional[socket.socket] = None
        self._running = False
        self._packet_pool = NetPacketPool()
        self._host: str = "0.0.0.0"
        self._port: int = 0
        self._max_peers: int = 10
        self._auto_recycle = True

        # Connection management / 连接管理
        self._connect_time: int = 0
        self._local_id: int = 0

    @property
    def peers_count(self) -> int:
        """Get number of connected peers / 获取已连接对等端数量"""
        return len(self._peers)

    @property
    def is_running(self) -> bool:
        """Check if manager is running / 检查管理器是否正在运行"""
        return self._running

    @property
    def local_port(self) -> int:
        """Get local port / 获取本地端口"""
        return self._port

    @property
    def listener(self) -> Optional[INetEventListener]:
        """Get event listener / 获取事件监听器"""
        return self._listener

    @listener.setter
    def listener(self, value: Optional[INetEventListener]) -> None:
        """Set event listener / 设置事件监听器"""
        self._listener = value

    def start(self, port: int = 0, host: str = "0.0.0.0", max_peers: int = 10) -> bool:
        """
        Start network manager / 启动网络管理器。

        Args:
            port: Local port to bind to (0 for any available port) / 要绑定的本地端口
            host: Local address to bind to / 要绑定的本地地址
            max_peers: Maximum number of peers / 最大对等端数量

        Returns:
            True if started successfully / 如果成功启动则返回 True
        """
        if self._running:
            return False

        self._host = host
        self._port = port
        self._max_peers = max_peers

        try:
            # Create UDP socket / 创建 UDP socket
            self._socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self._socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self._socket.bind((host, port))

            # Get actual port if 0 was specified / 如果指定了 0，获取实际端口
            if port == 0:
                self._port = self._socket.getsockname()[1]

            self._running = True
            self._connect_time = NetUtils.get_time_ticks()
            self._local_id = NetUtils.generate_connect_id()

            return True
        except Exception as e:
            if self._socket:
                self._socket.close()
                self._socket = None
            print(f"Failed to start manager: {e}")
            return False

    def stop(self) -> None:
        """Stop network manager and disconnect all peers / 停止网络管理器并断开所有对等端"""
        if not self._running:
            return

        # Disconnect all peers / 断开所有对等端
        for peer in list(self._peers.values()):
            peer.disconnect()

        self._running = False

        if self._socket:
            self._socket.close()
            self._socket = None

        self._peers.clear()

    def connect(self, host: str, port: int, connection_data: Optional[bytes] = None) -> bool:
        """
        Connect to remote host / 连接到远程主机。

        Args:
            host: Remote host address / 远程主机地址
            port: Remote port / 远程端口
            connection_data: Optional connection data / 可选的连接数据

        Returns:
            True if connection initiated successfully / 如果成功发起连接则返回 True
        """
        if not self._running:
            return False

        address = (host, port)
        if address in self._peers:
            return False

        # Create peer / 创建对等端
        peer = NetPeer(self, address, 0)
        self._peers[address] = peer

        # Send connect request / 发送连接请求
        peer.send_connect_request(connection_data or b'')

        return True

    def get_peer_by_address(self, host: str, port: int) -> Optional[NetPeer]:
        """
        Get peer by address / 通过地址获取对等端。

        Args:
            host: Peer host address / 对等端主机地址
            port: Peer port / 对等端端口

        Returns:
            NetPeer if found, None otherwise / 找到则返回 NetPeer，否则返回 None
        """
        return self._peers.get((host, port))

    def send_to_all(
        self,
        data: bytes,
        delivery_method: Any = None,
        exclude_peer: Optional[NetPeer] = None
    ) -> None:
        """
        Send data to all connected peers / 向所有已连接的对等端发送数据。

        Args:
            data: Data to send / 要发送的数据
            delivery_method: Delivery method / 传输方法
            exclude_peer: Peer to exclude from sending / 要排除的对等端
        """
        for peer in self._peers.values():
            if peer != exclude_peer and peer.is_connected:
                peer.send(data, delivery_method)

    async def poll_async(self) -> None:
        """
        Async poll for network events / 异步轮询网络事件。

        This method should be called in an async context to process network events.
        此方法应在异步上下文中调用以处理网络事件。
        """
        if not self._running or not self._socket:
            return

        try:
            # Set socket to non-blocking / 设置 socket 为非阻塞
            self._socket.setblocking(False)

            while self._running:
                try:
                    # Receive data / 接收数据
                    data, addr = self._socket.recvfrom(NetConstants.MAX_PACKET_SIZE)
                    await self._handle_packet(data, addr)
                except BlockingIOError:
                    # No data available, wait a bit / 无可用数据，等待一下
                    await asyncio.sleep(0.001)
                except Exception as e:
                    print(f"Error receiving data: {e}")

                # Update peers / 更新对等端
                current_time = NetUtils.get_time_millis()
                for peer in list(self._peers.values()):
                    await peer.update_async(current_time)

        except Exception as e:
            print(f"Error in poll_async: {e}")

    async def _handle_packet(self, data: bytes, addr: tuple) -> None:
        """
        Handle received packet / 处理接收到的数据包。

        Args:
            data: Packet data / 数据包数据
            addr: Sender address / 发送者地址
        """
        try:
            packet = NetPacket.from_bytes(data)

            if not packet.verify():
                return

            peer = self._peers.get(addr)

            # Handle packet based on property / 根据属性处理数据包
            prop = packet.packet_property

            if prop == PacketProperty.CONNECT_REQUEST:
                await self._handle_connect_request(packet, addr)
            elif prop == PacketProperty.CONNECT_ACCEPT:
                if peer:
                    await peer.handle_connect_accept(packet)
            elif prop == PacketProperty.DISCONNECT:
                if peer:
                    await self._handle_disconnect(peer, packet)
            elif prop == PacketProperty.ACK:
                if peer:
                    await peer.handle_ack(packet)
            elif prop in [PacketProperty.CHANNELED, PacketProperty.UNRELIABLE]:
                if peer:
                    await peer.handle_data_packet(packet)
            else:
                # Other packet types / 其他数据包类型
                if peer:
                    await peer.process_packet(packet)

        except Exception as e:
            print(f"Error handling packet from {addr}: {e}")

    async def _handle_connect_request(self, packet: NetPacket, addr: tuple) -> None:
        """
        Handle connection request / 处理连接请求。

        Args:
            packet: Connection request packet / 连接请求数据包
            addr: Sender address / 发送者地址
        """
        from litenetlib.core.internal_packets import NetConnectRequestPacket

        request = NetConnectRequestPacket.from_data(packet)
        if not request:
            return

        # Check if we can accept more peers / 检查是否可以接受更多对等端
        if len(self._peers) >= self._max_peers:
            # Send reject / 发送拒绝
            self._send_reject(addr)
            return

        # Check protocol ID / 检查协议 ID
        protocol_id = NetConnectRequestPacket.get_protocol_id(packet)
        if protocol_id != NetConstants.PROTOCOL_ID:
            # Send invalid protocol / 发送无效协议
            self._send_invalid_protocol(addr)
            return

        # Create connection request event / 创建连接请求事件
        conn_request = ConnectionRequest(self, addr, request)

        if self._listener:
            # Let listener decide / 让监听器决定
            if self._listener.on_connection_request(conn_request):
                # Accepted / 已接受
                peer = NetPeer(self, addr, request.connection_number)
                self._peers[addr] = peer
                await peer.accept_connection(request)
            else:
                # Rejected / 已拒绝
                conn_request.reject()
        else:
            # Auto-accept / 自动接受
            peer = NetPeer(self, addr, request.connection_number)
            self._peers[addr] = peer
            await peer.accept_connection(request)

    async def _handle_disconnect(self, peer: NetPeer, packet: NetPacket) -> None:
        """
        Handle disconnect packet / 处理断开连接数据包。

        Args:
            peer: Peer that disconnected / 断开连接的对等端
            packet: Disconnect packet / 断开连接数据包
        """
        addr = peer.address
        peer.shutdown()

        if addr in self._peers:
            del self._peers[addr]

        if self._listener:
            self._listener.on_peer_disconnect(peer, DisconnectReason.REMOTE_CONNECTION_CLOSE)

    def _send_reject(self, addr: tuple) -> None:
        """Send connection reject / 发送连接拒绝"""
        packet = NetPacket(PacketProperty.DISCONNECT, 8)
        # Write reject reason / 写入拒绝原因
        if self._socket:
            self._socket.sendto(packet.get_bytes(), addr)

    def _send_invalid_protocol(self, addr: tuple) -> None:
        """Send invalid protocol response / 发送无效协议响应"""
        packet = NetPacket(PacketProperty.INVALID_PROTOCOL)
        if self._socket:
            self._socket.sendto(packet.get_bytes(), addr)

    def get_packet_from_pool(self, size: int) -> NetPacket:
        """Get packet from pool / 从池中获取数据包"""
        return self._packet_pool.get(size)

    def recycle_packet(self, packet: NetPacket) -> None:
        """Recycle packet to pool / 将数据包回收至池中"""
        self._packet_pool.recycle(packet)

    def __del__(self):
        """Cleanup on destruction / 销毁时清理"""
        self.stop()
