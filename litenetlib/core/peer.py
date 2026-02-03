"""
Network peer for LiteNetLib v0.9.5.2 / LiteNetLib v0.9.5.2 网络对等端

Represents a connected peer in the network.
表示网络中的已连接对等端。

Ported from: LiteNetLib/NetPeer.cs (v0.9.5.2)
"""

import asyncio
from typing import Optional, Tuple, Any, TYPE_CHECKING
from enum import IntFlag
from litenetlib.core.constants import (
    NetConstants, PacketProperty, DeliveryMethod,
    DisconnectReason
)
from litenetlib.core.packet import NetPacket
from litenetlib.core.internal_packets import (
    NetConnectRequestPacket, NetConnectAcceptPacket,
    serialize_address, deserialize_address
)
from litenetlib.utils.net_utils import NetUtils
from litenetlib.utils.data_writer import NetDataWriter

if TYPE_CHECKING:
    from litenetlib.core.manager import LiteNetManager


class ConnectionState(IntFlag):
    """
    Peer connection state / 对等端连接状态。

    C# Reference: ConnectionState enum
    """
    OUTGOING = 1 << 1
    CONNECTED = 1 << 2
    SHUTDOWN_REQUESTED = 1 << 3
    DISCONNECTED = 1 << 4
    ANY = OUTGOING | CONNECTED | SHUTDOWN_REQUESTED


class NetPeer:
    """
    Network peer class / 网络对等端类

    Manages connection to a single remote peer.
    管理到单个远程对等端的连接。

    C# Reference: NetPeer
    """

    def __init__(
        self,
        manager: 'LiteNetManager',
        address: Tuple[str, int],
        connection_number: int = 0
    ):
        """
        Create network peer / 创建网络对等端。

        Args:
            manager: Network manager / 网络管理器
            address: Remote address (host, port) / 远程地址
            connection_number: Connection number (0-3) / 连接编号
        """
        self._manager = manager
        self._address = address
        self._connection_number = connection_number
        self._state = ConnectionState.OUTGOING
        self._connect_time = 0
        self._remote_id = 0
        self._last_receive_time = NetUtils.get_time_millis()

        # Channels / 通道
        self._channels = {}
        self._pending_packets = []

        # Statistics / 统计
        self._ping = 0
        self._rtt = 0
        self._packet_loss = 0.0

    @property
    def address(self) -> Tuple[str, int]:
        """Get peer address / 获取对等端地址"""
        return self._address

    @property
    def connection_number(self) -> int:
        """Get connection number / 获取连接编号"""
        return self._connection_number

    @property
    def state(self) -> ConnectionState:
        """Get connection state / 获取连接状态"""
        return self._state

    @property
    def is_connected(self) -> bool:
        """Check if peer is connected / 检查对等端是否已连接"""
        return self._state == ConnectionState.CONNECTED

    @property
    def ping(self) -> int:
        """Get current ping in milliseconds / 获取当前 ping（毫秒）"""
        return self._ping

    @property
    def rtt(self) -> int:
        """Get round-trip time in milliseconds / 获取往返时间（毫秒）"""
        return self._rtt

    def send_connect_request(self, connection_data: bytes) -> None:
        """
        Send connection request / 发送连接请求。

        Args:
            connection_data: Additional connection data / 额外连接数据
        """
        self._connect_time = NetUtils.get_time_ticks()

        # Serialize address / 序列化地址
        host, port = self._address
        address_bytes = serialize_address(host, port)

        # Create connect request packet / 创建连接请求数据包
        packet = NetConnectRequestPacket.make(
            connect_data=connection_data,
            address_bytes=address_bytes,
            connect_id=self._connect_time
        )

        packet.connection_number = self._connection_number

        # Send packet / 发送数据包
        self._send_raw(packet)

    async def accept_connection(self, request: NetConnectRequestPacket) -> None:
        """
        Accept connection request / 接受连接请求。

        Args:
            request: Connection request / 连接请求
        """
        self._connect_time = request.connection_time
        self._connection_number = request.connection_number

        # Send connect accept / 发送连接接受
        packet = NetConnectAcceptPacket.make(
            connect_id=self._connect_time,
            connect_num=self._connection_number,
            reused_peer=False
        )

        self._send_raw(packet)

        # Update state / 更新状态
        self._state = ConnectionState.CONNECTED

        # Notify listener / 通知监听器
        if self._manager.listener:
            self._manager.listener.on_peer_connected(self)

    async def handle_connect_accept(self, packet: NetPacket) -> None:
        """
        Handle connection accept / 处理连接接受。

        Args:
            packet: Connect accept packet / 连接接受数据包
        """
        accept = NetConnectAcceptPacket.from_data(packet)
        if not accept:
            return

        self._connect_time = accept.connection_id
        self._connection_number = accept.connection_number

        # Update state / 更新状态
        self._state = ConnectionState.CONNECTED

        # Notify listener / 通知监听器
        if self._manager.listener:
            self._manager.listener.on_peer_connected(self)

    def send(
        self,
        data: bytes,
        delivery_method: Any = DeliveryMethod.RELIABLE_ORDERED
    ) -> None:
        """
        Send data to peer / 向对等端发送数据。

        Args:
            data: Data to send / 要发送的数据
            delivery_method: Delivery method / 传输方法
        """
        if not self.is_connected:
            return

        # For now, use simple implementation / 现在使用简单实现
        if delivery_method == DeliveryMethod.UNRELIABLE:
            self._send_unreliable(data)
        else:
            self._send_reliable(data)

    def _send_unreliable(self, data: bytes) -> None:
        """Send unreliable packet / 发送不可靠数据包"""
        packet = NetPacket(PacketProperty.UNRELIABLE, len(data))
        packet._data[packet.get_header_size():] = data
        self._send_raw(packet)

    def _send_reliable(self, data: bytes) -> None:
        """Send reliable packet / 发送可靠数据包"""
        # For simplicity, use channeled packet / 为简单起见，使用通道数据包
        packet = NetPacket(PacketProperty.CHANNELED, len(data))
        packet._data[packet.get_header_size():] = data
        self._send_raw(packet)

    def _send_raw(self, packet: NetPacket) -> None:
        """
        Send raw packet / 发送原始数据包。

        Args:
            packet: Packet to send / 要发送的数据包
        """
        if self._manager._socket:
            packet.connection_number = self._connection_number
            try:
                self._manager._socket.sendto(packet.get_bytes(), self._address)
            except Exception as e:
                print(f"Error sending packet: {e}")

    async def handle_ack(self, packet: NetPacket) -> None:
        """
        Handle ACK packet / 处理 ACK 数据包。

        Args:
            packet: ACK packet / ACK 数据包
        """
        # TODO: Implement ACK handling / TODO: 实现 ACK 处理
        pass

    async def handle_data_packet(self, packet: NetPacket) -> None:
        """
        Handle data packet / 处理数据数据包。

        Args:
            packet: Data packet / 数据数据包
        """
        if not self.is_connected:
            return

        # Extract data / 提取数据
        data = packet.get_data()

        # Notify listener / 通知监听器
        if self._manager.listener:
            from litenetlib.utils.data_reader import NetDataReader
            reader = NetDataReader(data)
            self._manager.listener.on_network_receive(self, reader)

    async def process_packet(self, packet: NetPacket) -> None:
        """
        Process incoming packet / 处理传入数据包。

        Args:
            packet: Packet to process / 要处理的数据包
        """
        prop = packet.packet_property

        if prop == PacketProperty.PING:
            await self._handle_ping(packet)
        elif prop == PacketProperty.PONG:
            await self._handle_pong(packet)
        elif prop == PacketProperty.MTU_CHECK:
            await self._handle_mtu_check(packet)
        elif prop == PacketProperty.MTU_OK:
            await self._handle_mtu_ok(packet)

    async def _handle_ping(self, packet: NetPacket) -> None:
        """Handle ping packet / 处理 ping 数据包"""
        # Send pong response / 发送 pong 响应
        pong = NetPacket(PacketProperty.PONG, 10)
        self._send_raw(pong)

    async def _handle_pong(self, packet: NetPacket) -> None:
        """Handle pong packet / 处理 pong 数据包"""
        # Calculate RTT / 计算 RTT
        current_time = NetUtils.get_time_millis()
        self._rtt = current_time - self._ping
        self._ping = self._rtt // 2

    async def _handle_mtu_check(self, packet: NetPacket) -> None:
        """Handle MTU check packet / 处理 MTU 检查数据包"""
        # Send MTU OK response / 发送 MTU OK 响应
        mtu_ok = NetPacket(PacketProperty.MTU_OK)
        self._send_raw(mtu_ok)

    async def _handle_mtu_ok(self, packet: NetPacket) -> None:
        """Handle MTU OK packet / 处理 MTU OK 数据包"""
        # MTU discovery complete / MTU 发现完成
        pass

    async def update_async(self, current_time: int) -> None:
        """
        Update peer state (async) / 更新对等端状态（异步）。

        Args:
            current_time: Current time in milliseconds / 当前时间（毫秒）
        """
        # Check for timeout / 检查超时
        if self.is_connected and current_time - self._last_receive_time > 30000:  # 30 second timeout
            self.shutdown()
            if self._manager.listener:
                self._manager.listener.on_peer_disconnect(self, DisconnectReason.TIMEOUT)

    def disconnect(self) -> None:
        """Disconnect from peer / 断开与对等端的连接"""
        if self._state == ConnectionState.DISCONNECTED:
            return

        # Send disconnect packet / 发送断开连接数据包
        packet = NetPacket(PacketProperty.DISCONNECT, 8)
        self._send_raw(packet)

        self.shutdown()

    def shutdown(self) -> None:
        """Shutdown peer connection / 关闭对等端连接"""
        self._state = ConnectionState.DISCONNECTED

    def __repr__(self) -> str:
        """String representation / 字符串表示"""
        return f"NetPeer(address={self._address}, state={self._state.name})"
