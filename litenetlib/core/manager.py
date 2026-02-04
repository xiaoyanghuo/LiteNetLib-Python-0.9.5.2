"""
Network manager for LiteNetLib v0.9.5.2 / LiteNetLib v0.9.5.2 网络管理器

Main class for all network operations. Can be used as client and/or server.
所有网络操作的主类。可以用作客户端和/或服务器。

Ported from: LiteNetLib/NetManager.cs (v0.9.5.2)
"""

import asyncio
import socket
import time
from typing import Dict, Optional, Set, Callable, Any, TYPE_CHECKING, Tuple
from litenetlib.core.constants import NetConstants, PacketProperty, DisconnectReason
from litenetlib.core.packet import NetPacket, NetPacketPool
from litenetlib.core.peer import NetPeer, ConnectionState
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

        # Configuration options / 配置选项
        self._channels_count: int = 2  # Default number of channels
        self._update_time: int = 15  # Update interval in ms
        self._ping_interval: int = 1000  # Ping interval in ms
        self._disconnect_timeout: int = 30000  # Disconnect timeout in ms
        self._max_connect_attempts: int = 5  # Maximum connection attempts
        self._reconnect_delay: int = 500  # Reconnect delay in ms
        self._unconnected_messages_enabled: bool = False
        self._nat_punch_enabled: bool = False
        self._broadcast_receive_enabled: bool = False
        self._mtu_override: int = 0  # 0 = auto
        self._mtu_discovery: bool = True
        self._ipv6_enabled: bool = False
        self._packet_merging_enabled: bool = True
        self._enable_statistics: bool = False

        # Statistics / 统计
        from litenetlib.core.statistics import NetStatistics
        self._statistics = NetStatistics()

    @property
    def peers_count(self) -> int:
        """Get number of connected peers / 获取已连接对等端数量"""
        return len(self._peers)

    @property
    def connected_peers_count(self) -> int:
        """Get number of connected peers / 获取已连接对等端数量（C# 兼容名称）"""
        return len([p for p in self._peers.values() if p.is_connected])

    @property
    def is_running(self) -> bool:
        """Check if manager is running / 检查管理器是否正在运行"""
        return self._running

    @property
    def local_port(self) -> int:
        """Get local port / 获取本地端口"""
        return self._port

    @property
    def auto_recycle(self) -> bool:
        """Get auto recycle setting / 获取自动回收设置"""
        return self._auto_recycle

    @auto_recycle.setter
    def auto_recycle(self, value: bool) -> None:
        """Set auto recycle setting / 设置自动回收设置"""
        self._auto_recycle = value

    @property
    def channels_count(self) -> int:
        """Get number of channels / 获取通道数量"""
        return self._channels_count

    @channels_count.setter
    def channels_count(self, value: int) -> None:
        """Set number of channels (1-64) / 设置通道数量"""
        self._channels_count = max(1, min(64, value))

    @property
    def first_peer(self) -> Optional[NetPeer]:
        """Get first connected peer / 获取第一个已连接对等端"""
        for peer in self._peers.values():
            if peer.is_connected:
                return peer
        return None

    @property
    def connected_peer_list(self) -> list:
        """Get list of connected peers / 获取已连接对等端列表"""
        return [p for p in self._peers.values() if p.is_connected]

    @property
    def ipv6_enabled(self) -> bool:
        """Get IPv6 enabled / 获取 IPv6 启用状态"""
        return self._ipv6_enabled

    @ipv6_enabled.setter
    def ipv6_enabled(self, value: bool) -> None:
        """Set IPv6 enabled / 设置 IPv6 启用状态"""
        self._ipv6_enabled = value

    @property
    def mtu_override(self) -> int:
        """Get MTU override / 获取 MTU 覆盖值"""
        return self._mtu_override

    @mtu_override.setter
    def mtu_override(self, value: int) -> None:
        """Set MTU override / 设置 MTU 覆盖值"""
        self._mtu_override = max(0, value)

    @property
    def mtu_discovery(self) -> bool:
        """Get MTU discovery enabled / 获取 MTU 发现启用状态"""
        return self._mtu_discovery

    @mtu_discovery.setter
    def mtu_discovery(self, value: bool) -> None:
        """Set MTU discovery enabled / 设置 MTU 发现启用状态"""
        self._mtu_discovery = value

    @property
    def packet_merging(self) -> bool:
        """Get packet merging enabled / 获取包合并启用状态"""
        return self._packet_merging_enabled

    @packet_merging.setter
    def packet_merging(self, value: bool) -> None:
        """Set packet merging enabled / 设置包合并启用状态"""
        self._packet_merging_enabled = value

    @property
    def unconnected_messages_enabled(self) -> bool:
        """Get unconnected messages enabled / 获取无连接消息启用状态"""
        return self._unconnected_messages_enabled

    @unconnected_messages_enabled.setter
    def unconnected_messages_enabled(self, value: bool) -> None:
        """Set unconnected messages enabled / 设置无连接消息启用状态"""
        self._unconnected_messages_enabled = value

    @property
    def nat_punch_enabled(self) -> bool:
        """Get NAT punch enabled / 获取 NAT 穿透启用状态"""
        return self._nat_punch_enabled

    @nat_punch_enabled.setter
    def nat_punch_enabled(self, value: bool) -> None:
        """Set NAT punch enabled / 设置 NAT 穿透启用状态"""
        self._nat_punch_enabled = value

    @property
    def broadcast_receive_enabled(self) -> bool:
        """Get broadcast receive enabled / 获取广播接收启用状态"""
        return self._broadcast_receive_enabled

    @broadcast_receive_enabled.setter
    def broadcast_receive_enabled(self, value: bool) -> None:
        """Set broadcast receive enabled / 设置广播接收启用状态"""
        self._broadcast_receive_enabled = value

    @property
    def update_time(self) -> int:
        """Get update interval / 获取更新间隔"""
        return self._update_time

    @update_time.setter
    def update_time(self, value: int) -> None:
        """Set update interval / 设置更新间隔"""
        self._update_time = max(1, value)

    @property
    def ping_interval(self) -> int:
        """Get ping interval / 获取 ping 间隔"""
        return self._ping_interval

    @ping_interval.setter
    def ping_interval(self, value: int) -> None:
        """Set ping interval / 设置 ping 间隔"""
        self._ping_interval = max(1, value)

    @property
    def disconnect_timeout(self) -> int:
        """Get disconnect timeout / 获取断开超时"""
        return self._disconnect_timeout

    @disconnect_timeout.setter
    def disconnect_timeout(self, value: int) -> None:
        """Set disconnect timeout / 设置断开超时"""
        self._disconnect_timeout = max(1000, value)

    @property
    def max_connect_attempts(self) -> int:
        """Get max connect attempts / 获取最大连接尝试次数"""
        return self._max_connect_attempts

    @max_connect_attempts.setter
    def max_connect_attempts(self, value: int) -> None:
        """Set max connect attempts / 设置最大连接尝试次数"""
        self._max_connect_attempts = max(1, value)

    @property
    def reconnect_delay(self) -> int:
        """Get reconnect delay / 获取重连延迟"""
        return self._reconnect_delay

    @reconnect_delay.setter
    def reconnect_delay(self, value: int) -> None:
        """Set reconnect delay / 设置重连延迟"""
        self._reconnect_delay = max(0, value)

    @property
    def enable_statistics(self) -> bool:
        """Get statistics enabled / 获取统计启用状态"""
        return self._enable_statistics

    @enable_statistics.setter
    def enable_statistics(self, value: bool) -> None:
        """Set statistics enabled / 设置统计启用状态"""
        self._enable_statistics = value

    @property
    def statistics(self):
        """Get network statistics / 获取网络统计"""
        return self._statistics

    @property
    def listener(self) -> Optional[INetEventListener]:
        """Get event listener / 获取事件监听器"""
        return self._listener

    @listener.setter
    def listener(self, value: Optional[INetEventListener]) -> None:
        """Set event listener / 设置事件监听器"""
        self._listener = value

    def start(
        self,
        port: int = 0,
        host: str = "0.0.0.0",
        max_peers: int = 10,
        address_ipv4: Optional[str] = None,
        address_ipv6: Optional[str] = None
    ) -> bool:
        """
        Start network manager / 启动网络管理器。

        Args:
            port: Local port to bind to (0 for any available port) / 要绑定的本地端口
            host: Local address to bind to / 要绑定的本地地址
            max_peers: Maximum number of peers / 最大对等端数量
            address_ipv4: IPv4 address (for dual stack) / IPv4 地址
            address_ipv6: IPv6 address (for dual stack) / IPv6 地址

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

    def stop(self, send_disconnect_messages: bool = True) -> None:
        """
        Stop network manager and disconnect all peers / 停止网络管理器并断开所有对等端。

        Args:
            send_disconnect_messages: Whether to send disconnect messages / 是否发送断开消息
        """
        if not self._running:
            return

        # Disconnect all peers / 断开所有对等端
        for peer in list(self._peers.values()):
            if send_disconnect_messages:
                peer.disconnect()
            else:
                peer.shutdown()

        self._running = False

        if self._socket:
            self._socket.close()
            self._socket = None

        self._peers.clear()

    def get_peers_count(self, state: Optional[ConnectionState] = None) -> int:
        """
        Get number of peers with specific state / 获取特定状态的对等端数量。

        Args:
            state: Connection state to count (None = all connected) / 要计数的连接状态

        Returns:
            Number of peers with specified state
        """
        if state is None:
            return self.connected_peers_count
        return len([p for p in self._peers.values() if p._state == state])

    def get_peers_non_alloc(self, state: Optional[ConnectionState] = None) -> list:
        """
        Get peers list without allocation (returns list instead of filling) / 获取对等端列表（无分配版本）。

        Args:
            state: Connection state filter / 连接状态过滤器

        Returns:
            List of peers with specified state
        """
        if state is None:
            return self.connected_peer_list
        return [p for p in self._peers.values() if p._state == state]

    def get_peer_by_id(self, peer_id: int) -> Optional[NetPeer]:
        """
        Get peer by ID / 通过 ID 获取对等端。

        Args:
            peer_id: Peer ID / 对等端 ID

        Returns:
            NetPeer if found, None otherwise
        """
        for peer in self._peers.values():
            if peer.id == peer_id:
                return peer
        return None

    def poll_events(self) -> None:
        """
        Poll for network events (sync version) / 轮询网络事件（同步版本）。

        This is a sync wrapper around async poll.
        这是异步轮询的同步包装器。
        """
        if not self._running or not self._socket:
            return

        try:
            self._socket.setblocking(False)

            # Receive and process available packets
            while self._running:
                try:
                    data, addr = self._socket.recvfrom(NetConstants.MAX_PACKET_SIZE)
                    # Process packet synchronously
                    asyncio.create_task(self._handle_packet(data, addr))
                except BlockingIOError:
                    break
                except Exception as e:
                    print(f"Error receiving data: {e}")
                    break

            # Update peers
            current_time = NetUtils.get_time_millis()
            for peer in list(self._peers.values()):
                # Sync update
                if asyncio.iscoroutinefunction(peer.update_async):
                    asyncio.create_task(peer.update_async(current_time))
                else:
                    peer.update(current_time)

        except Exception as e:
            print(f"Error in poll_events: {e}")

    def __iter__(self):
        """Get iterator over peers / 获取对等端迭代器"""
        return iter(self._peers.values())
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

    def connect(
        self,
        address,
        port: Optional[int] = None,
        key: Optional[str] = None,
        connection_data: Optional[bytes] = None,
        data: Optional[bytes] = None
    ) -> Optional[NetPeer]:
        """
        Connect to remote host / 连接到远程主机。

        Args:
            address: Remote host address (str) or tuple (host, port) / 远程主机地址
            port: Remote port (if address is string) / 远程端口
            key: Connection key string / 连接密钥字符串
            connection_data: Optional connection data bytes / 可选连接数据字节
            data: Alias for connection_data / connection_data 的别名

        Returns:
            NetPeer if connection initiated successfully, None otherwise / 成功返回 NetPeer，否则返回 None
        """
        if not self._running:
            return None

        # Parse address
        if isinstance(address, tuple):
            host, port_num = address
        else:
            host = address
            port_num = port if port is not None else 0

        address = (host, port_num)
        if address in self._peers:
            return self._peers[address]

        # Prepare connection data
        conn_data = connection_data or data
        if key is not None:
            from litenetlib.utils.data_writer import NetDataWriter
            writer = NetDataWriter()
            writer.put_string(key)
            conn_data = writer.to_bytes()
        elif conn_data is None:
            conn_data = b''

        # Create peer / 创建对等端
        peer = NetPeer(self, address, 0)
        self._peers[address] = peer

        # Send connect request / 发送连接请求
        peer.send_connect_request(conn_data)

        return peer

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
        data,
        delivery_method: Any = None,
        exclude_peer: Optional[NetPeer] = None,
        channel_number: int = 0
    ) -> None:
        """
        Send data to all connected peers / 向所有已连接的对等端发送数据。

        Args:
            data: Data to send (bytes or NetDataWriter) / 要发送的数据
            delivery_method: Delivery method / 传输方法
            exclude_peer: Peer to exclude from sending / 要排除的对等端
            channel_number: Channel number / 通道编号
        """
        for peer in self._peers.values():
            if peer != exclude_peer and peer.is_connected:
                peer.send(data, delivery_method, channel_number)

    def send_unconnected_message(
        self,
        message,
        address: Optional[Tuple[str, int]] = None,
        host: Optional[str] = None,
        port: Optional[int] = None
    ) -> None:
        """
        Send unconnected message / 发送无连接消息。

        Args:
            message: Message to send (bytes or NetDataWriter) / 要发送的消息
            address: Target address (host, port) / 目标地址
            host: Target host / 目标主机
            port: Target port / 目标端口
        """
        if not self._running or not self._socket:
            return

        # Parse address
        if address is None:
            if host is not None and port is not None:
                address = (host, port)
            else:
                raise ValueError("Either address or host+port must be provided")

        # Get message bytes
        if isinstance(message, NetDataWriter):
            data = message.to_bytes()
        else:
            data = message

        try:
            self._socket.sendto(data, address)
        except Exception as e:
            print(f"Error sending unconnected message: {e}")

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
