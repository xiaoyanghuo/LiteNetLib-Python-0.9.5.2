"""
ReliableChannel.cs 翻译（完整版）

可靠通道 - 实现ACK/NACK协议的可靠交付

C#源文件: ReliableChannel.cs
C#行数: ~335行
实现状态: ✓完整
最后更新: 2025-02-05
说明: 完整实现了C#版本的所有功能，包括滑动窗口、ACK处理、包重传
"""

from typing import List, Optional, TYPE_CHECKING
import threading

from .base_channel import BaseChannel

if TYPE_CHECKING:
    from ..lite_net_peer import LiteNetPeer
    from ..packets.net_packet import NetPacket
    from ..constants import DeliveryMethod, NetConstants


class PendingPacket:
    """
    待发送包结构

    C#定义: private struct PendingPacket
    C#源位置: ReliableChannel.cs:7-51

    用于存储待确认的包，支持重传机制
    """

    def __init__(self):
        self._packet: Optional['NetPacket'] = None
        self._time_stamp: int = 0
        self._is_sent: bool = False

    def init(self, packet: 'NetPacket') -> None:
        """
        初始化待发送包

        C#方法: public void Init(NetPacket packet)
        C#源位置: ReliableChannel.cs:15-19

        参数:
            packet: NetPacket - 要初始化的包
        """
        self._packet = packet
        self._is_sent = False

    def try_send(self, current_time: int, peer: 'LiteNetPeer') -> bool:
        """
        尝试发送包（带重传检查）

        C#方法: public bool TrySend(long currentTime, LiteNetPeer peer)
        C#源位置: ReliableChannel.cs:22-39

        参数:
            current_time: int - 当前时间（ticks）
            peer: LiteNetPeer - 目标peer

        返回:
            bool: 如果有包待发送返回true，否则返回false
        """
        if self._packet is None:
            return False

        if self._is_sent:  # 检查发送时间
            # 转换：peer.ResendDelay (double ms) → ticks
            resend_delay_ticks = int(peer.resend_delay * 10000)  # ms to ticks
            packet_hold_time = current_time - self._time_stamp

            if packet_hold_time < resend_delay_ticks:
                return True  # 还没到重发时间

            # 需要重发
            from ..debug import NetDebug
            NetDebug.write(f"[RC]Resend: {packet_hold_time} > {resend_delay_ticks}")

        self._time_stamp = current_time
        self._is_sent = True

        # 发送包
        peer.send_user_data(self._packet)
        return True

    def clear(self, peer: 'LiteNetPeer') -> bool:
        """
        清理包（已确认，可回收）

        C#方法: public bool Clear(LiteNetPeer peer)
        C#源位置: ReliableChannel.cs:41-50

        参数:
            peer: LiteNetPeer - 目标peer

        返回:
            bool: 如果清理了包返回true，否则返回false
        """
        if self._packet is not None:
            peer.recycle_and_deliver(self._packet)
            self._packet = None
            return True
        return False

    def __repr__(self) -> str:
        """字符串表示"""
        if self._packet is None:
            return "Empty"
        return f"Packet(seq={self._packet.sequence})"


class ReliableChannel(BaseChannel):
    """
    可靠通道

    C#定义: internal sealed class ReliableChannel : BaseChannel
    C#源位置: ReliableChannel.cs:5-334

    实现可靠有序/无序的包交付：
    - ACK/NACK协议
    - 滑动窗口协议
    - 包重传
    - 丢包检测
    - 有序/无序模式
    """

    BITS_IN_BYTE = 8

    def __init__(self, peer: 'LiteNetPeer', ordered: bool, id: int):
        """
        创建可靠通道

        C#构造函数: public ReliableChannel(LiteNetPeer peer, bool ordered, byte id)
        C#源位置: ReliableChannel.cs:71-96

        参数:
            peer: LiteNetPeer - 所属的peer
            ordered: bool - 是否为有序模式
            id: int - 通道ID
        """
        super().__init__(peer)

        self._peer = peer
        self._id = id

        # 窗口大小
        self._window_size = NetConstants.default_window_size
        self._ordered = ordered

        # 待发送包数组（滑动窗口）
        self._pending_packets: List[PendingPacket] = [
            PendingPacket() for _ in range(self._window_size)
        ]
        self._pending_packets_lock = threading.Lock()

        # 接收包数组
        if self._ordered:
            self._received_packets: List[Optional['NetPacket']] = [
                None for _ in range(self._window_size)
            ]
            self._delivery_method = DeliveryMethod.ReliableOrdered
        else:
            self._early_received: List[bool] = [
                False for _ in range(self._window_size)
            ]
            self._delivery_method = DeliveryMethod.ReliableUnordered

        # 序列号
        self._local_sequence = 0
        self._remote_sequence = 0
        self._local_window_start = 0
        self._remote_window_start = 0

        # ACK包
        from ..packets.net_packet import NetPacket, PacketProperty
        ack_size = (self._window_size - 1) // self.BITS_IN_BYTE + 2
        self._outgoing_acks = NetPacket(PacketProperty.Ack, ack_size)
        self._outgoing_acks.channel_id = id
        self._outgoing_acks_lock = threading.Lock()

        # 标志
        self._must_send_acks = False

        # 出队队列（由peer管理）
        self.outgoing_queue = []

    @property
    def peer(self) -> 'LiteNetPeer':
        """获取所属peer"""
        return self._peer

    @property
    def delivery_method(self) -> 'DeliveryMethod':
        """获取交付方式"""
        return self._delivery_method

    def send_next_packets(self) -> bool:
        """
        发送下一个包

        C#方法: public override bool SendNextPackets()
        C#源位置: ReliableChannel.cs:165-207

        返回:
            bool: 如果有待处理的包返回true
        """
        from ..packets.net_packet import PacketProperty

        # 发送ACK
        if self._must_send_acks:
            self._must_send_acks = False
            from ..debug import NetDebug
            NetDebug.write("[RR]SendAcks")
            with self._outgoing_acks_lock:
                self._peer.send_user_data(self._outgoing_acks)

        # 当前时间（ticks）
        import time
        current_time = int(time.time() * 10000000)  # 转换为ticks
        has_pending_packets = False

        with self._pending_packets_lock:
            # 从队列获取包
            while self.outgoing_queue:
                relate = self._relative_sequence_number(
                    self._local_sequence,
                    self._local_window_start
                )
                if relate >= self._window_size:
                    break

                packet = self.outgoing_queue.pop(0)
                packet.sequence = self._local_sequence
                packet.channel_id = self._id
                self._pending_packets[
                    self._local_sequence % self._window_size
                ].init(packet)
                self._local_sequence = (self._local_sequence + 1) % NetConstants.max_sequence

            # 发送待发送的包
            pending_seq = self._local_window_start
            while pending_seq != self._local_sequence:
                idx = pending_seq % self._window_size
                # 注意：TrySend修改了struct的字段，必须直接调用
                if self._pending_packets[idx].try_send(current_time, self._peer):
                    has_pending_packets = True
                pending_seq = (pending_seq + 1) % NetConstants.max_sequence

        return has_pending_packets or self._must_send_acks or len(self.outgoing_queue) > 0

    def process_packet(self, packet: 'NetPacket') -> bool:
        """
        处理收到的包

        C#方法: public override bool ProcessPacket(NetPacket packet)
        C#源位置: ReliableChannel.cs:210-332

        参数:
            packet: NetPacket - 收到的包

        返回:
            bool: 如果包被处理返回true
        """
        from ..packets.net_packet import PacketProperty
        from ..debug import NetDebug

        # 处理ACK包
        if packet.packet_property == PacketProperty.Ack:
            self._process_ack(packet)
            return False

        seq = packet.sequence

        # 验证序列号
        if seq >= NetConstants.max_sequence:
            NetDebug.write("[RR]Bad sequence")
            return False

        relate = self._relative_sequence_number(seq, self._remote_window_start)
        relate_seq = self._relative_sequence_number(seq, self._remote_sequence)

        if relate_seq > self._window_size:
            NetDebug.write("[RR]Bad sequence")
            return False

        # 丢弃坏包
        if relate < 0:
            NetDebug.write("[RR]ReliableInOrder too old")
            return False
        if relate >= self._window_size * 2:
            NetDebug.write("[RR]ReliableInOrder too new")
            return False

        # 处理新窗口位置
        ack_idx = seq % self._window_size
        ack_byte = NetConstants.channeled_header_size + ack_idx // self.BITS_IN_BYTE
        ack_bit = ack_idx % self.BITS_IN_BYTE

        with self._outgoing_acks_lock:
            if relate >= self._window_size:
                # 新窗口位置
                new_window_start = (
                    self._remote_window_start + relate - self._window_size + 1
                ) % NetConstants.max_sequence
                self._outgoing_acks.sequence = new_window_start

                # 清理旧数据
                while self._remote_window_start != new_window_start:
                    old_idx = self._remote_window_start % self._window_size
                    old_byte = NetConstants.channeled_header_size + old_idx // self.BITS_IN_BYTE
                    old_bit = old_idx % self.BITS_IN_BYTE
                    self._outgoing_acks.raw_data[old_byte] &= ~(1 << old_bit)
                    self._remote_window_start = (
                        self._remote_window_start + 1
                    ) % NetConstants.max_sequence

            # 触发ACK发送
            self._must_send_acks = True

            # 检查重复
            if (self._outgoing_acks.raw_data[ack_byte] & (1 << ack_bit)) != 0:
                NetDebug.write("[RR]ReliableInOrder duplicate")
                if hasattr(self, 'add_to_peer_channel_send_queue'):
                    self.add_to_peer_channel_send_queue()
                return False

            # 保存ACK
            self._outgoing_acks.raw_data[ack_byte] |= (1 << ack_bit)

        if hasattr(self, 'add_to_peer_channel_send_queue'):
            self.add_to_peer_channel_send_queue()

        # 详细检查
        if seq == self._remote_sequence:
            NetDebug.write("[RR]ReliableInOrder packet success")
            self._peer.add_reliable_packet(self._delivery_method, packet)
            self._remote_sequence = (self._remote_sequence + 1) % NetConstants.max_sequence

            # 处理缓存的包
            if self._ordered:
                while self._received_packets[self._remote_sequence % self._window_size] is not None:
                    # 处理缓存的包
                    p = self._received_packets[self._remote_sequence % self._window_size]
                    self._received_packets[self._remote_sequence % self._window_size] = None
                    self._peer.add_reliable_packet(self._delivery_method, p)
                    self._remote_sequence = (self._remote_sequence + 1) % NetConstants.max_sequence
            else:
                while self._early_received[self._remote_sequence % self._window_size]:
                    # 处理早期接收的包
                    self._early_received[self._remote_sequence % self._window_size] = False
                    self._peer.add_reliable_packet(self._delivery_method, packet)
                    self._remote_sequence = (self._remote_sequence + 1) % NetConstants.max_sequence

            return True

        # 缓存包
        if self._ordered:
            self._received_packets[ack_idx] = packet
        else:
            self._early_received[ack_idx] = True
            self._peer.add_reliable_packet(self._delivery_method, packet)

        return True

    def _process_ack(self, packet: 'NetPacket') -> None:
        """
        处理ACK包

        C#方法: private void ProcessAck(NetPacket packet)
        C#源位置: ReliableChannel.cs:99-163

        参数:
            packet: NetPacket - ACK包
        """
        from ..debug import NetDebug
        from ..packets.net_packet import PacketProperty

        # 验证包大小
        if packet.size != self._outgoing_acks.size:
            NetDebug.write("[PA]Invalid acks packet size")
            return

        ack_window_start = packet.sequence
        window_rel = self._relative_sequence_number(self._local_window_start, ack_window_start)

        if ack_window_start >= NetConstants.max_sequence or window_rel < 0:
            NetDebug.write("[PA]Bad window start")
            return

        # 检查相关性
        if window_rel >= self._window_size:
            NetDebug.write("[PA]Old acks")
            return

        acks_data = packet.raw_data

        with self._pending_packets_lock:
            # 处理窗口中的包
            pending_seq = self._local_window_start
            while pending_seq != self._local_sequence:
                rel = self._relative_sequence_number(pending_seq, ack_window_start)
                if rel >= self._window_size:
                    NetDebug.write(f"[PA]REL: {rel}")
                    break

                pending_idx = pending_seq % self._window_size
                current_byte = NetConstants.channeled_header_size + pending_idx // self.BITS_IN_BYTE
                current_bit = pending_idx % self.BITS_IN_BYTE

                if (acks_data[current_byte] & (1 << current_bit)) == 0:
                    # 未收到ACK，丢包统计
                    if self._peer.net_manager.enable_statistics:
                        self._peer.statistics.increment_packet_loss()
                        self._peer.net_manager.statistics.increment_packet_loss()

                    NetDebug.write(f"[PA]False ack: {pending_seq}")
                    pending_seq = (pending_seq + 1) % NetConstants.max_sequence
                    continue

                # 收到ACK，清理包
                if pending_seq == self._local_window_start:
                    # 移动窗口
                    self._local_window_start = (self._local_window_start + 1) % NetConstants.max_sequence

                # 清理包
                if self._pending_packets[pending_idx].clear(self._peer):
                    NetDebug.write(f"[PA]Removing reliableInOrder ack: {pending_seq} - true")

                pending_seq = (pending_seq + 1) % NetConstants.max_sequence

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
    "PendingPacket",
    "ReliableChannel",
]
