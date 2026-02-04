"""
Network peer for LiteNetLib v0.9.5.2 / LiteNetLib v0.9.5.2 网络对等端

Represents a connected peer in the network.
表示网络中的已连接对等端。

Ported from: LiteNetLib/NetPeer.cs (v0.9.5.2)
"""

import asyncio
import time
from typing import Optional, Tuple, Any, TYPE_CHECKING, List
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
from litenetlib.core.fragments import (
    FragmentPool, IncomingFragment,
    create_fragment_packet, parse_fragment_header
)
from litenetlib.core.mtu_discovery import MtuDiscovery
from litenetlib.core.packet_merging import MergedPacket, process_merged_packet
from litenetlib.utils.net_utils import NetUtils
from litenetlib.utils.data_writer import NetDataWriter
from litenetlib.channels.base_channel import BaseChannel
from litenetlib.channels.reliable_channel import ReliableChannel
from litenetlib.channels.sequenced_channel import SequencedChannel

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
        # Each channel type can have 2 channels (channel_number 0 or 1)
        # C#: BaseChannel[] _channels = new BaseChannel[ChannelsCount * 2]
        self._channels: List[Optional[BaseChannel]] = [None] * (NetConstants.MAX_CONNECTION_NUMBER * 2)
        self._channel_send_queue: List[BaseChannel] = []

        # Pending packets for delivery events
        self._pending_packets = []

        # Statistics / 统计
        self._ping = 0
        self._rtt = 0
        self._packet_loss = 0.0

        # RTT calculation
        self._rtt_reset_time = 0
        self._last_packet_send_time = 0
        self._resent_packets = 0

        # MTU
        self._mtu = NetConstants.INITIAL_MTU
        self._mtu_discovery = MtuDiscovery()

        # Ping/Pong
        self._ping_send_time = 0
        self._ping_interval = 1000  # Send ping every 1 second (ms)
        self._last_ping_send_time = 0  # Last time we sent a ping (ms)
        self._max_ping_attempts = 5  # Max failed pings before disconnect
        self._ping_attempts = 0  # Current failed ping attempts

        # Resend delay (dynamic based on RTT)
        self._resend_delay = 300  # Initial 300ms

        # Fragments / 分片
        self._fragment_pool = FragmentPool(timeout=5.0)
        self._fragment_id = 0  # Fragment group ID counter

        # Packet merging / 包合并
        self._merge_packet = MergedPacket(max_size=NetConstants.MAX_PACKET_SIZE)

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
        # C# return _rtt / 2;
        return self._rtt // 2

    @property
    def rtt(self) -> int:
        """Get round-trip time in milliseconds / 获取往返时间（毫秒）"""
        return self._rtt

    @property
    def id(self) -> int:
        """Get peer ID / 获取对等端 ID"""
        return self._remote_id

    @property
    def remote_id(self) -> int:
        """Get remote peer ID / 获取远程对等端 ID"""
        return self._remote_id

    @property
    def mtu(self) -> int:
        """
        Get MTU value / 获取 MTU 值

        Returns current MTU from discovery or manually set value.
        返回 MTU 发现的当前值或手动设置的值。
        """
        # If discovery is complete, use discovered MTU
        # C#: return _mtu;
        if self._mtu_discovery.is_discovery_complete:
            return self._mtu_discovery.get_max_safe_mtu()
        return self._mtu

    @mtu.setter
    def mtu(self, value: int) -> None:
        """
        Set MTU value / 设置 MTU 值

        Args:
            value: New MTU value / 新的 MTU 值
        """
        # Clamp to valid range
        self._mtu = max(NetConstants.INITIAL_MTU, min(value, NetConstants.MAX_PACKET_SIZE))

        # Reset discovery if MTU is manually set
        if self._mtu_discovery.is_discovery_complete and self._mtu != value:
            self._mtu_discovery.reset()

    @property
    def resend_delay(self) -> int:
        """
        Get resend delay in milliseconds / 获取重发延迟（毫秒）

        C# Reference: public int ResendDelay => _rtt * 2 + 100;
        """
        # C#: return _rtt * 2 + 100;
        rtt_value = max(self._rtt, 50)  # Minimum 50ms
        return rtt_value * 2 + 100

    @property
    def remote_time_delta(self) -> int:
        """Get remote time delta / 获取远程时间差"""
        return 0  # TODO: Implement time synchronization

    @property
    def remote_utc_time(self) -> int:
        """Get remote UTC time / 获取远程 UTC 时间"""
        return NetUtils.get_time_ticks() + self.remote_time_delta

    @property
    def time_since_last_packet(self) -> int:
        """Get time since last received packet / 获取距离上次接收的时间"""
        return NetUtils.get_time_millis() - self._last_receive_time

    @property
    def tag(self) -> Any:
        """Get user tag / 获取用户标签"""
        return getattr(self, '_tag', None)

    @tag.setter
    def tag(self, value: Any) -> None:
        """Set user tag / 设置用户标签"""
        self._tag = value

    @property
    def statistics(self):
        """Get network statistics / 获取网络统计"""
        if not hasattr(self, '_statistics'):
            from litenetlib.core.statistics import NetStatistics
            self._statistics = NetStatistics()
        return self._statistics

    # Channel helper methods / 通道辅助方法

    def _get_or_create_channel(self, delivery_method: DeliveryMethod, channel_number: int) -> BaseChannel:
        """
        Get or create channel for delivery method and channel number.

        Args:
            delivery_method: Delivery method / 传输方法
            channel_number: Channel number (0-1) / 通道编号

        Returns:
            Channel instance / 通道实例

        C# Reference: NetPeer.GetOrCreateChannel()
        """
        # Calculate channel index
        # C#: Each channel type can have 2 channels
        #     chanNum 0, method ReliableOrdered -> _channels[0]
        #     chanNum 1, method ReliableOrdered -> _channels[2]
        idx = channel_number * 2

        if delivery_method == DeliveryMethod.RELIABLE_ORDERED:
            # C#: return _channels[idx] ?? (_channels[idx] = new ReliableChannel(this, true, (byte)idx))
            if self._channels[idx] is None:
                self._channels[idx] = ReliableChannel(self, ordered=True, channel_id=idx)
            return self._channels[idx]
        elif delivery_method == DeliveryMethod.SEQUENCED:
            # C#: return _channels[idx + 1] ?? (_channels[idx + 1] = new SequencedChannel(this, false, (byte)(idx + 1)))
            if self._channels[idx + 1] is None:
                self._channels[idx + 1] = SequencedChannel(self, reliable=False, channel_id=idx + 1)
            return self._channels[idx + 1]
        elif delivery_method == DeliveryMethod.RELIABLE_UNORDERED:
            # C#: return _channels[idx + 2] ?? (_channels[idx + 2] = new ReliableChannel(this, false, (byte)(idx + 2)))
            if self._channels[idx + 2] is None:
                self._channels[idx + 2] = ReliableChannel(self, ordered=False, channel_id=idx + 2)
            return self._channels[idx + 2]
        elif delivery_method == DeliveryMethod.RELIABLE_SEQUENCED:
            # C#: return _channels[idx + 1] ?? (_channels[idx + 1] = new SequencedChannel(this, true, (byte)(idx + 1)))
            if self._channels[idx + 1] is None:
                self._channels[idx + 1] = SequencedChannel(self, reliable=True, channel_id=idx + 1)
            return self._channels[idx + 1]
        else:
            # UNRELIABLE - no channel
            raise ValueError(f"UNRELIABLE delivery method doesn't use channels")

    def add_channel_to_send_queue(self, channel: BaseChannel) -> None:
        """
        Add channel to peer's send queue.

        Args:
            channel: Channel to add / 要添加的通道

        C# Reference: NetPeer.AddToReliableChannelSendQueue()
        """
        if channel not in self._channel_send_queue:
            self._channel_send_queue.append(channel)

    def send_user_data(self, packet: NetPacket) -> None:
        """
        Send user data packet (called by channels).

        Args:
            packet: Packet to send / 要发送的数据包

        C# Reference: NetPeer.SendUserData()
        """
        self._send_raw(packet)
        self._last_packet_send_time = NetUtils.get_time_millis()

    def add_reliable_packet(self, delivery_method: DeliveryMethod, packet: NetPacket) -> None:
        """
        Add received reliable packet to delivery queue.

        Args:
            delivery_method: Delivery method / 传输方法
            packet: Received packet / 接收的数据包

        C# Reference: NetPeer.AddReliablePacket()
        """
        # Extract data from packet
        data = packet.get_data()

        # Notify listener
        if self._manager.listener:
            from litenetlib.utils.data_reader import NetDataReader
            reader = NetDataReader(data)

            # Calculate channel number from channel_id
            # C#: byte channelNumber = (byte)(packet.ChannelId / ChannelTypeCount)
            channel_number = packet.channel_id // 2

            self._manager.listener.on_network_receive(
                self, reader, channel_number, delivery_method
            )

    def recycle_and_deliver(self, packet: NetPacket) -> None:
        """
        Recycle packet to pool and trigger delivery event.

        Args:
            packet: Packet to recycle / 要回收的数据包

        C# Reference: NetPeer.RecycleAndDeliver()
        """
        # Python doesn't use packet pool, so just ignore
        # C#: NetManager.PoolRecycle(packet)
        pass

    @property
    def connection_state(self) -> ConnectionState:
        """Get connection state / 获取连接状态"""
        return self._state

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
        data,
        delivery_method: Any = DeliveryMethod.RELIABLE_ORDERED,
        channel_number: int = 0,
        start: int = 0,
        length: Optional[int] = None,
        options: Any = None
    ) -> None:
        """
        Send data to peer / 向对等端发送数据。

        Args:
            data: Data to send (bytes or NetDataWriter) / 要发送的数据
            delivery_method: Delivery method / 传输方法
            channel_number: Channel number / 通道编号
            start: Start offset in data / 数据起始偏移
            length: Number of bytes to send / 要发送的字节数
            options: Additional options / 额外选项（兼容 C# 参数）
        """
        if not self.is_connected:
            return

        # Validate channel number
        # C#: if (channelNumber >= MaxChannelNumber) throw new ArgumentOutOfRangeException
        if channel_number >= NetConstants.MAX_CONNECTION_NUMBER:
            raise ValueError(f"Channel number must be < {NetConstants.MAX_CONNECTION_NUMBER}")

        # Handle NetDataWriter
        if isinstance(data, NetDataWriter):
            data_bytes = data.to_bytes()
        elif isinstance(data, (bytes, bytearray)):
            data_bytes = data
        else:
            raise TypeError(f"Unsupported data type: {type(data)}")

        # Apply offset and length if specified
        if start > 0 or length is not None:
            if length is None:
                length = len(data_bytes) - start
            data_bytes = data_bytes[start:start + length]

        # Route based on delivery method
        if delivery_method == DeliveryMethod.UNRELIABLE:
            # Send unreliable packet directly
            packet = NetPacket(PacketProperty.UNRELIABLE, len(data_bytes))
            packet._data[packet.get_header_size():] = data_bytes

            # Try to merge small packets
            # C#: if (_packetMerger != null && _packetMerger.TryMergePacket(packet, currentTime))
            if self._manager._packet_merging_enabled:
                if not self._merge_packet.add_packet(packet, time.time()):
                    # Merge failed, send directly
                    self.send_user_data(packet)
            else:
                self.send_user_data(packet)
        else:
            # Send through channel
            channel = self._get_or_create_channel(delivery_method, channel_number)

            # Check if fragmentation needed
            # C#: int maxPacketSize = MTU - _mtuCheckAttempts;
            max_packet_size = self.mtu - NetConstants.CHANNELED_HEADER_SIZE

            if len(data_bytes) > max_packet_size:
                # Need to fragment
                # C#: SendFragmented(data, ...)
                self._send_fragmented(data_bytes, delivery_method, channel_number, channel)
            else:
                # Create single packet
                # C#: var packet = NetManager.PoolRentWithProperty(PacketProperty.Channeled, size)
                packet = NetPacket(PacketProperty.CHANNELED, len(data_bytes))

                # Write data to packet (skip header)
                # C#: Buffer.BlockCopy(data, start, packet.RawData, packet.GetHeaderSize(), length)
                packet._data[packet.get_header_size():] = data_bytes

                # Try to merge small packets
                # C#: if (_packetMerger != null && _packetMerger.TryMergePacket(packet, currentTime))
                if self._manager._packet_merging_enabled:
                    if not self._merge_packet.add_packet(packet, time.time()):
                        # Merge failed, send through channel
                        channel.add_to_queue(packet)
                else:
                    channel.add_to_queue(packet)

    def send_with_delivery_event(
        self,
        data,
        delivery_method: Any = DeliveryMethod.RELIABLE_ORDERED,
        channel_number: int = 0,
        user_data: Any = None
    ) -> None:
        """
        Send data with delivery event callback / 发送数据并触发送达事件。

        Args:
            data: Data to send / 要发送的数据
            delivery_method: Delivery method / 传输方法
            channel_number: Channel number / 通道编号
            user_data: User data to pass to delivery event / 传递给送达事件的用户数据

        Note: Python implementation uses callbacks instead of C# events.
              Delivery events are handled through the listener.
        """
        # TODO: Implement delivery event tracking
        self.send(data, delivery_method, channel_number)

    def _send_fragmented(
        self,
        data: bytes,
        delivery_method: DeliveryMethod,
        channel_number: int,
        channel: BaseChannel
    ) -> None:
        """
        Send data as fragments.

        Args:
            data: Data to send / 要发送的数据
            delivery_method: Delivery method / 传输方法
            channel_number: Channel number / 通道编号
            channel: Channel to use / 要使用的通道

        C# Reference: NetPeer.SendFragmented
        """
        # Calculate fragment size
        # C#: int maxPacketSize = MTU - _mtuCheckAttempts - PacketProperty.Channeled.GetHeaderSize();
        max_packet_size = self.mtu - NetConstants.CHANNELED_HEADER_SIZE - NetConstants.FRAGMENT_HEADER_SIZE

        # Calculate number of fragments
        # C#: int fragmentCount = data.Length / maxPacketSize + 1;
        fragment_count = (len(data) + max_packet_size - 1) // max_packet_size

        # Get fragment group ID
        # C#: ushort fragmentId = ++_fragmentId;
        self._fragment_id = (self._fragment_id + 1) % 65536
        fragment_id = self._fragment_id

        # Send fragments
        # C#: for (int i = 0; i < fragmentCount; i++)
        for i in range(fragment_count):
            # Calculate fragment offset and size
            offset = i * max_packet_size
            remaining = len(data) - offset
            fragment_size = min(max_packet_size, remaining)

            # Get fragment data
            fragment_data = data[offset:offset + fragment_size]

            # Create fragment packet
            # C#: var packet = NetManager.PoolRentWithProperty(PacketProperty.Channeled, ...);
            #     packet.SetFragmented(true);
            #     packet.ChannelId = (byte)((fragmentId * NetConstants.MaxChannelTypeCount) + channelId);
            fragment_packet = create_fragment_packet(
                fragment_data,
                fragment_id,
                i,
                fragment_count,
                channel_number * 2  # Convert channel number to channel ID
            )

            # Add to channel queue
            # C#: _channels[(byte)((fragmentId * NetConstants.MaxChannelTypeCount) + channelId)].AddToQueue(packet);
            channel.add_to_queue(fragment_packet)

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

    async def handle_data_packet(self, packet: NetPacket) -> None:
        """
        Handle data packet / 处理数据数据包。

        Args:
            packet: Data packet / 数据数据包
        """
        if not self.is_connected:
            return

        # Route based on packet property
        prop = packet.packet_property

        if prop == PacketProperty.UNRELIABLE:
            # Unreliable packet - deliver directly
            data = packet.get_data()
            if self._manager.listener:
                from litenetlib.utils.data_reader import NetDataReader
                reader = NetDataReader(data)
                self._manager.listener.on_network_receive(
                    self, reader, 0, DeliveryMethod.UNRELIABLE
                )
        elif prop == PacketProperty.CHANNELED:
            # Check if fragmented
            # C#: if (packet.IsFragmented)
            if packet.is_fragmented:
                # Process fragment
                await self._process_fragment(packet)
            else:
                # Channeled packet - route to appropriate channel
                # C#: GetChannelByPacketId(packet)
                channel = self._get_channel_by_packet_id(packet)
                if channel is not None:
                    channel.process_packet(packet)

    async def _process_fragment(self, packet: NetPacket) -> None:
        """
        Process incoming fragment packet.

        Args:
            packet: Fragment packet / 分片数据包

        C# Reference: NetPeer.ProcessPacket (fragment handling)
        """
        # Parse fragment header
        # C#: ushort fragmentId = FastBitConverter.ToUInt16(...);
        #     ushort fragmentPart = FastBitConverter.ToUInt16(...);
        #     ushort fragmentTotal = FastBitConverter.ToUInt16(...);
        fragment_id, fragment_part, fragment_total = parse_fragment_header(packet)

        # Get or create fragment group
        # C#: _incomingFragments.TryGetValue(fragmentId, out var fragments)
        fragments = self._fragment_pool.get_fragments(fragment_id)

        if fragments is None:
            # First fragment - calculate total size
            # C#: int totalSize = packet.Size - PacketProperty.GetHeaderSize(PacketProperty.Channeled, ...) + (fragmentTotal - 1) * MTU;
            header_size = NetConstants.CHANNELED_HEADER_SIZE + NetConstants.FRAGMENT_HEADER_SIZE
            first_fragment_size = packet.size - header_size

            # Estimate total size (will be corrected as fragments arrive)
            # C#: var fragments = new IncomingFragments(fragmentTotal, totalSize);
            estimated_total = first_fragment_size + (fragment_total - 1) * (self.mtu - header_size)
            fragments = self._fragment_pool.create_fragments(fragment_id, fragment_total, estimated_total)

            # Set first fragment packet (contains delivery info)
            fragments.set_first_fragment(packet)

        # Add fragment data
        # Extract fragment data (skip header and fragment header)
        header_size = NetConstants.CHANNELED_HEADER_SIZE + NetConstants.FRAGMENT_HEADER_SIZE
        fragment_data = packet._data[header_size:]

        # C#: if (!fragments.Add(fragmentPart, data))
        if not fragments.add_fragment(fragment_part, fragment_data):
            # Duplicate fragment - ignore
            return

        # Check if all fragments arrived
        # C#: if (fragments.IsReady)
        if fragments.is_complete():
            # Assemble packet
            # C#: var assembledPacket = fragments.Assemble();
            assembled_packet = fragments.assemble()
            if assembled_packet:
                # Get delivery method from first fragment
                # C#: var finalPacket = new NetPacket(...);
                # Process as normal packet
                if self._manager.listener:
                    from litenetlib.utils.data_reader import NetDataReader
                    reader = NetDataReader(assembled_packet.get_data())
                    channel_number = packet.channel_id // 2
                    self._manager.listener.on_network_receive(
                        self, reader, channel_number, DeliveryMethod.RELIABLE_ORDERED
                    )

            # Remove fragment group
            # C#: _incomingFragments.Remove(fragmentId);
            self._fragment_pool.remove_fragments(fragment_id)

    async def _process_merged(self, packet: NetPacket) -> None:
        """
        Process merged packet / 处理合并数据包

        Args:
            packet: Merged packet / 合并数据包

        C# Reference: NetPeer.ProcessPacket (MERGED handling)
        """
        # Extract individual packets from merged packet
        # C#: var packets = ProcessMergedPacket(packet);
        packets = process_merged_packet(packet)

        # Process each extracted packet
        # C#: foreach (var p in packets)
        for extracted_packet in packets:
            # Process as normal packet
            # C#: ProcessPacket(p);
            await self.process_packet(extracted_packet)

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
        elif prop == PacketProperty.ACK:
            # Route to channel
            channel = self._get_channel_by_packet_id(packet)
            if channel is not None:
                channel.process_packet(packet)
        elif prop == PacketProperty.CHANNELED:
            # Check if fragmented
            # C#: if (packet.IsFragmented)
            if packet.is_fragmented:
                # Process fragment
                await self._process_fragment(packet)
            else:
                # Route to channel
                channel = self._get_channel_by_packet_id(packet)
                if channel is not None:
                    channel.process_packet(packet)
        elif prop == PacketProperty.MERGED:
            # Process merged packet
            # C#: ProcessMergedPacket(packet)
            await self._process_merged(packet)
        elif prop == PacketProperty.MTU_CHECK:
            await self._handle_mtu_check(packet)
        elif prop == PacketProperty.MTU_OK:
            await self._handle_mtu_ok(packet)

    def _get_channel_by_packet_id(self, packet: NetPacket) -> Optional[BaseChannel]:
        """
        Get channel by packet ID.

        Args:
            packet: Packet to get channel for / 要获取通道的数据包

        Returns:
            Channel or None / 通道或None

        C# Reference: NetPeer.GetChannelByPacketId()
        """
        channel_id = packet.channel_id
        if channel_id < len(self._channels):
            return self._channels[channel_id]
        return None

    async def _handle_ping(self, packet: NetPacket) -> None:
        """
        Handle ping packet / 处理 ping 数据包。

        C# Reference: NetPeer.OnPingReceived()
        """
        # Send pong response / 发送 pong 响应
        pong = NetPacket(PacketProperty.PONG, 10)
        self._send_raw(pong)

    async def _handle_pong(self, packet: NetPacket) -> None:
        """
        Handle pong packet / 处理 pong 数据包。

        C# Reference: NetPeer.OnPongReceived()
        """
        # Calculate RTT / 计算 RTT
        current_time = NetUtils.get_time_millis()

        # C#: _rtt = currentTime - _pingSendTime;
        if self._ping_send_time != 0:
            new_rtt = current_time - self._ping_send_time

            # C#: _rtt = (_rtt * 3 + newRtt) / 4; // Weighted average
            self._rtt = (self._rtt * 3 + new_rtt) // 4
            self._ping = self._rtt // 2

            # C#: _rttResetTime = currentTime;
            self._rtt_reset_time = current_time

            # Reset ping attempts (received pong)
            self._ping_attempts = 0
            self._ping_send_time = 0

            # Notify latency update
            # C#: NetManager.OnPeerLatencyUpdate(this, _rtt)
            if self._manager and self._manager.listener:
                self._manager.listener.on_network_latency_update(self, self._rtt)

    def send_ping(self) -> None:
        """
        Send ping packet to peer / 向对等端发送 ping 数据包。

        C# Reference: NetPeer.SendPing() / Update() ping logic
        """
        current_time = NetUtils.get_time_millis()

        # C#: var pingPacket = new NetPacket(PacketProperty.Ping, 4);
        ping = NetPacket(PacketProperty.PING, 4)

        # Record send time / 记录发送时间
        # C#: _pingSendTime = currentTime;
        self._ping_send_time = current_time
        self._last_ping_send_time = current_time

        # Send ping / 发送 ping
        self._send_raw(ping)

        # Increment attempts / 增加尝试次数
        self._ping_attempts += 1

    async def _handle_mtu_check(self, packet: NetPacket) -> None:
        """
        Handle MTU check packet / 处理 MTU 检查数据包

        Called when remote peer sends us an MTU probe.
        当远程对等端向我们发送 MTU 探测包时调用。

        Args:
            packet: MTU check packet / MTU 检查数据包

        C# Reference: NetPeer.ProcessPacket (MTU_CHECK handling)
        """
        # The packet size itself indicates the MTU being tested
        # C#: int mtu = packet.Size;
        mtu = packet.size

        # Send MTU OK response to confirm we received this size
        # C#: var packet = new NetPacket(PacketProperty.MtuOk, 0);
        mtu_ok = NetPacket(PacketProperty.MTU_OK, 0)
        self._send_raw(mtu_ok)

        # Could also update our MTU based on received probe size
        # if we want to support asymmetric MTU
        # C#: if (mtu > _mtu) _mtu = mtu;
        if mtu > self._mtu:
            self._mtu = min(mtu, NetConstants.MAX_PACKET_SIZE)

    async def _handle_mtu_ok(self, packet: NetPacket) -> None:
        """
        Handle MTU OK packet / 处理 MTU OK 数据包

        Called when remote peer successfully received our MTU probe.
        当远程对等端成功接收我们的 MTU 探测包时调用。

        Args:
            packet: MTU OK packet / MTU OK 数据包

        C# Reference: NetPeer.ProcessPacket (MTU_OK handling)
        """
        # Get current MTU being tested
        current_mtu = self._mtu_discovery.get_next_mtu()
        if current_mtu:
            # Record successful MTU
            # C#: _mtu = currentMtu;
            self._mtu_discovery.handle_success(current_mtu)

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
                self._manager.listener.on_peer_disconnected(self, DisconnectReason.TIMEOUT)

        # Process channel send queue
        # C#: while (_channelSendQueue.Count > 0)
        while self._channel_send_queue:
            # C#: _channelSendQueue[0].SendNextPackets()
            channel = self._channel_send_queue[0]
            has_more = channel.send_next_packets()

            # C#: if (!hasMore) _channelSendQueue.RemoveAt(0)
            if not has_more:
                self._channel_send_queue.pop(0)
                channel.mark_sent()
            else:
                # Move to back of queue
                # C#: _channelSendQueue.RemoveAt(0); _channelSendQueue.Add(channel)
                self._channel_send_queue.pop(0)
                self._channel_send_queue.append(channel)

        # Update RTT
        # C#: if (_rttResetTime != 0 && currentTime - _rttResetTime > 1000)
        if self._rtt_reset_time != 0 and current_time - self._rtt_reset_time > 1000:
            self._rtt = 0
            self._rtt_reset_time = 0

        # Cleanup expired fragments
        # C#: _incomingFragments.CheckExpiry(...)
        self._fragment_pool.cleanup_expired()

        # MTU discovery / MTU 发现
        if self.is_connected and self._manager._mtu_discovery:
            # Check for timeout on current MTU probe
            # C#: if (currentTime - _mtuCheckTime > _mtuCheckAttempts * 1000 + 1000)
            if self._mtu_discovery.should_try_next(current_time):
                # Current MTU probe timed out, try smaller MTU
                pass  # handle_failure() already called by should_try_next

            # Send MTU probe if needed
            # C#: if (_mtuIdx + 1 < PossibleMtu.Count && currentTime - _mtuCheckTime > 1000)
            if self._mtu_discovery.start_check(current_time):
                probe_packet = self._mtu_discovery.send_probe(current_time)
                if probe_packet:
                    self._send_raw(probe_packet)

        # Packet merging / 包合并
        if self.is_connected and self._manager._packet_merging_enabled:
            # C#: if (_packetMerger != null && _packetMerger.NeedToSend())
            if self._merge_packet.should_send:
                # Send merged packet
                # C#: SendMerged(_packetMerger);
                merged = self._merge_packet.create_merged_packet()
                if merged:
                    self._send_raw(merged)

        # Ping/Pong mechanism / Ping/Pong 机制
        if self.is_connected:
            # Check if we need to send ping
            # C#: if (currentTime - _lastReceiveTime > _pingSendInterval)
            time_since_last_receive = current_time - self._last_receive_time

            # Send ping if:
            # 1. It's been ping_interval since last ping, AND
            # 2. We haven't received any data for ping_interval (to avoid unnecessary pings)
            if (current_time - self._last_ping_send_time >= self._ping_interval and
                time_since_last_receive >= self._ping_interval):
                self.send_ping()

            # Check for ping timeout (too many failed pings)
            # C#: if (_pingAttempts > NetConstants.MaxPingAttempts)
            if self._ping_attempts >= self._max_ping_attempts:
                # Connection lost / 连接丢失
                self.shutdown()
                if self._manager.listener:
                    self._manager.listener.on_peer_disconnected(self, DisconnectReason.TIMEOUT)

    def disconnect(
        self,
        data: Optional[bytes] = None,
        start: int = 0,
        count: Optional[int] = None
    ) -> None:
        """
        Disconnect from peer / 断开与对等端的连接。

        Args:
            data: Optional disconnect data / 可选断开数据
            start: Start offset in data / 数据起始偏移
            count: Number of bytes from data / 要使用的字节数
        """
        if self._state == ConnectionState.DISCONNECTED:
            return

        # Send disconnect packet / 发送断开连接数据包
        if data is not None:
            if count is None:
                count = len(data) - start
            packet = NetPacket(PacketProperty.DISCONNECT, 8 + count)
            # Write data to packet
            packet_data = packet.get_bytes()
            # TODO: Properly write data to packet
        else:
            packet = NetPacket(PacketProperty.DISCONNECT, 8)
        self._send_raw(packet)

        self.shutdown()

    def get_packets_count_in_reliable_queue(self, ordered: bool) -> int:
        """
        Get packet count in reliable queue / 获取可靠队列中的包数量。

        Args:
            ordered: Whether to count ordered packets only / 是否只计算有序包

        Returns:
            Number of packets in queue / 队列中的包数量

        C# Reference: NetPeer.GetPacketsCountInReliableQueue()
        """
        # C#: int count = 0;
        #     foreach (var c in _channels)
        #     {
        #         if (c != null && ((c is ReliableChannel rc && rc.Ordered == ordered) || ...))
        #             count += c.PacketsInQueue;
        #     }
        count = 0
        for channel in self._channels:
            if channel is None:
                continue
            if ordered:
                # Check if reliable ordered channel
                if isinstance(channel, ReliableChannel) and channel._ordered:
                    count += channel.packets_in_queue
            else:
                # Check if reliable unordered channel
                if isinstance(channel, ReliableChannel) and not channel._ordered:
                    count += channel.packets_in_queue
        return count

    def get_max_single_packet_size(self, delivery_method: Any) -> int:
        """
        Get maximum single packet size for delivery method / 获取单包最大大小。

        Args:
            delivery_method: Delivery method / 传输方法

        Returns:
            Maximum packet size in bytes
        """
        # Account for headers
        if delivery_method == DeliveryMethod.UNRELIABLE:
            return self.mtu - 1  # Property byte
        else:
            return self.mtu - 4  # Property + sequence + channel

    def shutdown(self) -> None:
        """
        Shutdown peer connection / 关闭对等端连接。

        C# Reference: NetPeer.Shutdown()
        """
        self._state = ConnectionState.DISCONNECTED

        # Clear channels / 清理通道
        # C#: for (int i = 0; i < _channels.Length; i++) _channels[i] = null;
        for i in range(len(self._channels)):
            self._channels[i] = None
        self._channel_send_queue.clear()

        # Clear fragments / 清理分片
        self._fragment_pool.clear()

        # Reset MTU discovery / 重置 MTU 发现
        self._mtu_discovery.reset()

        # Clear packet merge buffer / 清理包合并缓冲区
        self._merge_packet.clear()

    def __repr__(self) -> str:
        """String representation / 字符串表示"""
        return f"NetPeer(address={self._address}, state={self._state.name})"
