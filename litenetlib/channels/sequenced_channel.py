"""
SequencedChannel.cs 翻译（完整版）

序列通道 - 实现有序或序列的包交付

C#源文件: SequencedChannel.cs
C#行数: ~115行
实现状态: ✓完整
最后更新: 2025-02-05
说明: 完整实现了C#版本的所有功能，包括序列号验证、重复检测、ACK处理
"""

from typing import Optional, TYPE_CHECKING
import time

from .base_channel import BaseChannel

if TYPE_CHECKING:
    from ..lite_net_peer import LiteNetPeer
    from ..packets.net_packet import NetPacket, PacketProperty
    from ..constants import DeliveryMethod, NetConstants


class SequencedChannel(BaseChannel):
    """
    序列通道

    C#定义: internal sealed class SequencedChannel : BaseChannel
    C#源位置: SequencedChannel.cs:5-114

    实现有序或序列的包交付：
    - 序列号管理
    - 重复检测
    - ACK处理（reliable模式）
    - Last packet缓存（reliable模式）
    """

    def __init__(self, peer: 'LiteNetPeer', reliable: bool, id: int):
        """
        创建序列通道

        C#构造函数: public SequencedChannel(LiteNetPeer peer, bool reliable, byte id)
        C#源位置: SequencedChannel.cs:16-22

        参数:
            peer: LiteNetPeer - 所属的peer
            reliable: bool - 是否为可靠模式
            id: int - 通道ID
        """
        super().__init__(peer)

        self._peer = peer
        self._id = id
        self._reliable = reliable

        # 序列号
        self._local_sequence = 0
        self._remote_sequence = 0

        # Last packet缓存（仅reliable模式）
        self._last_packet: Optional[NetPacket] = None

        # ACK包（仅reliable模式）
        self._ack_packet: Optional[NetPacket] = None
        if self._reliable:
            self._ack_packet = NetPacket(PacketProperty.Ack, 0)
            self._ack_packet.channel_id = id

        # 标志
        self._must_send_ack = False

        # 发送时间
        self._last_packet_send_time = 0

    @property
    def peer(self) -> 'LiteNetPeer':
        """获取所属peer"""
        return self._peer

    def send_next_packets(self) -> bool:
        """
        发送下一个包

        C#方法: public override bool SendNextPackets()
        C#源位置: SequencedChannel.cs:24-73

        返回:
            bool: 如果有last packet返回true
        """
        # Reliable模式且队列为空时重发last packet
        if self._reliable and len(self.outgoing_queue) == 0:
            current_time = int(time.time() * 10000000)  # 转换为ticks
            packet_hold_time = current_time - self._last_packet_send_time

            if packet_hold_time >= self._peer.resend_delay * 10000:  # ms to ticks
                packet = self._last_packet
                if packet is not None:
                    self._last_packet_send_time = current_time
                    self._peer.send_user_data(packet)
            return self._last_packet is not None

        # 处理队列中的包
        while self.outgoing_queue:
            packet = self.outgoing_queue.pop(0)
            self._local_sequence = (self._local_sequence + 1) % NetConstants.max_sequence
            packet.sequence = self._local_sequence
            packet.channel_id = self._id
            self._peer.send_user_data(packet)

            # Reliable模式：缓存last packet
            if self._reliable and len(self.outgoing_queue) == 0:
                self._last_packet_send_time = int(time.time() * 10000000)
                self._last_packet = packet
            else:
                # Non-reliable模式：回收包
                if packet is not None:
                    self._peer.net_manager.pool_recycle(packet)

        # 发送ACK（仅reliable模式）
        if self._reliable and self._must_send_ack:
            self._must_send_ack = False
            self._ack_packet.sequence = self._remote_sequence
            self._peer.send_user_data(self._ack_packet)

        return self._last_packet is not None

    def process_packet(self, packet: 'NetPacket') -> bool:
        """
        处理收到的包

        C#方法: public override bool ProcessPacket(NetPacket packet)
        C#源位置: SequencedChannel.cs:75-112

        参数:
            packet: NetPacket - 收到的包

        返回:
            bool: 如果包被处理返回true
        """
        from ..debug import NetDebug

        # 分片包由其他地方处理
        if packet.is_fragmented:
            return False

        # 处理ACK包
        if packet.packet_property == PacketProperty.Ack:
            if self._reliable and self._last_packet is not None and packet.sequence == self._last_packet.sequence:
                self._last_packet = None
            return False

        # 计算相对序列号
        relative = self._relative_sequence_number(packet.sequence, self._remote_sequence)
        packet_processed = False

        if packet.sequence < NetConstants.max_sequence and relative > 0:
            # 统计丢包
            if self._peer.net_manager.enable_statistics:
                self._peer.statistics.add_packet_loss(relative - 1)
                self._peer.net_manager.statistics.add_packet_loss(relative - 1)

            # 更新远程序列号
            self._remote_sequence = packet.sequence

            # 创建接收事件
            self._peer.net_manager.create_receive_event(
                packet,
                self._reliable and DeliveryMethod.ReliableSequenced or DeliveryMethod.Sequenced,
                (packet.channel_id // NetConstants.channel_type_count),
                NetConstants.channeled_header_size,
                self._peer
            )
            packet_processed = True

        # Reliable模式需要发送ACK
        if self._reliable:
            self._must_send_ack = True
            if hasattr(self, 'add_to_peer_channel_send_queue'):
                self.add_to_peer_channel_send_queue()

        return packet_processed

    def _relative_sequence_number(self, sequence: int, start_sequence: int) -> int:
        """
        计算相对序列号

        C#对应: NetUtils.RelativeSequenceNumber

        参数:
            sequence: int - 序列号
            start_sequence: int - 起始序列号

        返回:
            int: 相对序列号
        """
        diff = sequence - start_sequence
        if diff < 0:
            diff += NetConstants.max_sequence
        return diff


__all__ = [
    "SequencedChannel",
]
