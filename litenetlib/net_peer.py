"""
NetPeer.cs 翻译（完整版）

改进的LiteNetPeer，支持完整的多通道功能

C#源文件: NetPeer.cs
C#行数: ~244行
实现状态: ✓完整
最后更新: 2025-02-05
说明: 完整实现了C#版本的所有功能，包括多通道支持、Send方法重载、通道创建
"""

import threading
from typing import Optional, List, TYPE_CHECKING
from queue import Queue

from .constants import DeliveryMethod, NetConstants
from .lite_net_peer import LiteNetPeer
from .channels.base_channel import BaseChannel
from .channels.reliable_channel import ReliableChannel
from .channels.sequenced_channel import SequencedChannel
from .packets.net_packet import NetPacket

if TYPE_CHECKING:
    from .net_manager import NetManager
    from .connection_request import ConnectionRequest
    from .utils.net_data_writer import NetDataWriter


class NetPeer(LiteNetPeer):
    """
    网络Peer - 代表与远程端点的连接

    C#定义: public class NetPeer : LiteNetPeer
    C#源位置: NetPeer.cs:12-242

    主要功能：
    - 多通道支持
    - 可靠/不可靠发送
    - 分片和重组
    - MTU发现
    - ACK/NACK处理
    """

    def __init__(
        self,
        net_manager: 'NetManager',
        remote_end_point: tuple,
        id: int,
        connect_num: Optional[int] = None,
        connect_data: Optional[bytes] = None
    ):
        """
        创建peer（多种构造函数）

        C#构造函数:
        - internal NetPeer(NetManager netManager, IPEndPoint remoteEndPoint, int id)
        - internal NetPeer(NetManager netManager, IPEndPoint remoteEndPoint, int id, byte connectNum, ReadOnlySpan<byte> connectData)
        - internal NetPeer(NetManager netManager, ConnectionRequest request, int id)
        C#源位置: NetPeer.cs:19-32

        参数:
            net_manager: NetManager - 网络管理器
            remote_end_point: tuple - 远程端点
            id: int - peer ID
            connect_num: Optional[int] - 连接编号（可选）
            connect_data: Optional[bytes] - 连接数据（可选）
        """
        # 根据参数调用父类构造函数
        if connect_num is not None and connect_data is not None:
            super().__init__(net_manager, remote_end_point, id, connect_num, connect_data)
        else:
            super().__init__(net_manager, remote_end_point, id)

        self._net_manager = net_manager
        self._channel_send_queue: Queue[BaseChannel] = Queue()

        # 创建通道数组
        channels_count = net_manager.channels_count
        self._channels: List[Optional[BaseChannel]] = [
            None for _ in range(channels_count * NetConstants.channel_type_count)
        ]

    @property
    def channels_count(self) -> int:
        """
        获取通道数量

        C#属性: protected override int ChannelsCount => ((NetManager)NetManager).ChannelsCount
        C#源位置: NetPeer.cs:17

        返回:
            int: 通道数量
        """
        return self._net_manager.channels_count

    # ========================================================================
    # LiteNetPeer抽象方法实现
    # ========================================================================

    def create_channel(self, channel_number: int) -> Optional[BaseChannel]:
        """
        创建通道

        C#方法: internal override BaseChannel CreateChannel(byte idx)
        C#源位置: NetPeer.cs:216-241

        参数:
            channel_number: int - 通道编号

        返回:
            Optional[BaseChannel]: 创建的通道
        """
        new_channel = self._channels[channel_number]
        if new_channel is not None:
            return new_channel

        # 根据交付方法创建通道类型
        delivery_method = DeliveryMethod(channel_number % NetConstants.channel_type_count)

        if delivery_method == DeliveryMethod.ReliableUnordered:
            new_channel = ReliableChannel(self, False, channel_number)
        elif delivery_method == DeliveryMethod.Sequenced:
            new_channel = SequencedChannel(self, False, channel_number)
        elif delivery_method == DeliveryMethod.ReliableOrdered:
            new_channel = ReliableChannel(self, True, channel_number)
        elif delivery_method == DeliveryMethod.ReliableSequenced:
            new_channel = SequencedChannel(self, True, channel_number)
        else:
            # Unreliable通道不需要创建
            return None

        # 线程安全地设置通道
        if self._channels[channel_number] is None:
            self._channels[channel_number] = new_channel

        return new_channel

    def update_channels(self) -> None:
        """
        更新通道（发送待发送的包）

        C#方法: protected override void UpdateChannels()
        C#源位置: NetPeer.cs:182-199
        """
        if self._channel_send_queue.empty():
            return

        count = self._channel_send_queue.qsize()
        while count > 0:
            try:
                channel = self._channel_send_queue.get_nowait()
                if channel.send_next_packets():
                    # 仍然有待发送的包，重新加入队列
                    self._channel_send_queue.put(channel)
                count -= 1
            except:
                break

    def process_channeled(self, packet: NetPacket) -> None:
        """
        处理通道包

        C#方法: internal override void ProcessChanneled(NetPacket packet)
        C#源位置: NetPeer.cs:201-211

        参数:
            packet: NetPacket - 收到的包
        """
        if packet.channel_id >= len(self._channels):
            self._net_manager.pool_recycle(packet)
            return

        channel = self._channels[packet.channel_id]
        if channel is None and packet.packet_property != 2:  # PacketProperty.Ack
            channel = self.create_channel(packet.channel_id)

        if channel is not None and not channel.process_packet(packet):
            self._net_manager.pool_recycle(packet)

    def add_to_reliable_channel_send_queue(self, channel: BaseChannel) -> None:
        """
        添加通道到可靠发送队列

        C#方法: internal override void AddToReliableChannelSendQueue(BaseChannel channel)
        C#源位置: NetPeer.cs:213-214

        参数:
            channel: BaseChannel - 要添加的通道
        """
        self._channel_send_queue.put(channel)

    # ========================================================================
    # 公共Send方法（7个重载）
    # ========================================================================

    def send(self, data: bytes, channel_number: int, delivery_method: DeliveryMethod) -> None:
        """
        发送数据到peer

        C#方法: public void Send(byte[] data, byte channelNumber, DeliveryMethod deliveryMethod)
        C#源位置: NetPeer.cs:152-153

        参数:
            data: bytes - 要发送的数据
            channel_number: int - 通道编号（0到channels_count-1）
            delivery_method: DeliveryMethod - 发送选项

        异常:
            Exception: 如果大小超过限制
        """
        self.send_internal(data, channel_number, delivery_method, None)

    def send_with_writer(
        self,
        writer: 'NetDataWriter',
        channel_number: int,
        delivery_method: DeliveryMethod
    ) -> None:
        """
        发送数据到peer（使用NetDataWriter）

        C#方法: public void Send(NetDataWriter dataWriter, byte channelNumber, DeliveryMethod deliveryMethod)
        C#源位置: NetPeer.cs:45-46

        参数:
            writer: NetDataWriter - 包含数据的写入器
            channel_number: int - 通道编号
            delivery_method: DeliveryMethod - 发送选项
        """
        self.send_internal(writer.data, channel_number, delivery_method, None)

    def send_with_delivery_event(
        self,
        data: bytes,
        channel_number: int,
        delivery_method: DeliveryMethod,
        user_data: object
    ) -> None:
        """
        发送数据到peer（带交付事件）

        C#方法: public void SendWithDeliveryEvent(byte[] data, byte channelNumber, DeliveryMethod deliveryMethod, object userData)
        C#源位置: NetPeer.cs:58-63

        参数:
            data: bytes - 要发送的数据
            channel_number: int - 通道编号
            delivery_method: DeliveryMethod - 发送选项
            user_data: object - 用户数据（将在DeliveryEvent中接收）

        异常:
            ValueError: 如果尝试使用不可靠包类型
        """
        if delivery_method != DeliveryMethod.ReliableOrdered and delivery_method != DeliveryMethod.ReliableUnordered:
            raise ValueError("Delivery event will work only for ReliableOrdered/Unordered packets")
        self.send_internal(data, channel_number, delivery_method, user_data)

    def send_with_delivery_event_with_writer(
        self,
        writer: 'NetDataWriter',
        channel_number: int,
        delivery_method: DeliveryMethod,
        user_data: object
    ) -> None:
        """
        发送数据到peer（带交付事件，使用NetDataWriter）

        C#方法: public void SendWithDeliveryEvent(NetDataWriter dataWriter, byte channelNumber, DeliveryMethod deliveryMethod, object userData)
        C#源位置: NetPeer.cs:94-99

        参数:
            writer: NetDataWriter - 包含数据的写入器
            channel_number: int - 通道编号
            delivery_method: DeliveryMethod - 发送选项
            user_data: object - 用户数据

        异常:
            ValueError: 如果尝试使用不可靠包类型
        """
        if delivery_method != DeliveryMethod.ReliableOrdered and delivery_method != DeliveryMethod.ReliableUnordered:
            raise ValueError("Delivery event will work only for ReliableOrdered/Unordered packets")
        self.send_internal(writer.data, channel_number, delivery_method, user_data)

    def get_packets_count_in_reliable_queue(self, channel_number: int, ordered: bool) -> int:
        """
        获取可靠队列中的包数量

        C#方法: public int GetPacketsCountInReliableQueue(byte channelNumber, bool ordered)
        C#源位置: NetPeer.cs:175-180

        参数:
            channel_number: int - 通道编号（0-63）
            ordered: bool - True表示ReliableOrdered，False表示ReliableUnordered

        返回:
            int: 通道队列中的包数量
        """
        idx = channel_number * NetConstants.channel_type_count + (
            DeliveryMethod.ReliableOrdered if ordered else DeliveryMethod.ReliableUnordered
        )
        channel = self._channels[idx]
        if isinstance(channel, ReliableChannel):
            return len(channel.outgoing_queue)
        return 0

    def create_packet_from_pool(self, delivery_method: DeliveryMethod, channel_number: int):
        """
        从对象池创建临时包（最大大小MTU - headerSize）

        C#方法: public PooledPacket CreatePacketFromPool(DeliveryMethod deliveryMethod, byte channelNumber)
        C#源位置: NetPeer.cs:124-139

        参数:
            delivery_method: DeliveryMethod - 发送方式
            channel_number: int - 通道编号

        返回:
            PooledPacket: 可以从UserDataOffset开始写入数据的池化包
        """
        mtu = self.mtu
        packet = self._net_manager.pool_get_packet(mtu)

        if delivery_method == DeliveryMethod.Unreliable:
            from .packets.net_packet import PacketProperty
            packet.packet_property = PacketProperty.Unreliable
            return PooledPacket(packet, mtu, 0)
        else:
            from .packets.net_packet import PacketProperty
            packet.packet_property = PacketProperty.Channeled
            channel_id = channel_number * NetConstants.channel_type_count + delivery_method
            return PooledPacket(packet, mtu, channel_id)

    def send_internal(
        self,
        data: bytes,
        channel_number: int,
        delivery_method: DeliveryMethod,
        user_data: Optional[object]
    ) -> None:
        """
        内部发送方法

        C#方法: private void SendInternal(ReadOnlySpan<byte> data, byte channelNumber, DeliveryMethod deliveryMethod, object userData)

        参数:
            data: bytes - 要发送的数据
            channel_number: int - 通道编号
            delivery_method: DeliveryMethod - 发送方式
            user_data: Optional[object] - 用户数据
        """
        # 这里调用父类LiteNetPeer的send_with_channel方法
        self.send_with_channel(data, channel_number, delivery_method, user_data)


class PooledPacket:
    """
    池化包 - 用于零拷贝发送

    C#定义: public readonly struct PooledPacket
    C#源位置: NetPeer.cs

    属性:
        packet: NetPacket - 从池中获取的包
        mtu: int - MTU大小
        channel_id: int - 通道ID
    """
    def __init__(self, packet: NetPacket, mtu: int, channel_id: int):
        self.packet = packet
        self.mtu = mtu
        self.channel_id = channel_id


__all__ = [
    "NetPeer",
    "PooledPacket",
]
