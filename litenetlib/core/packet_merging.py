"""
Packet merging for LiteNetLib.

Implements packet merging to combine multiple small packets into one large packet.
实现数据包合并，将多个小包合并成一个大包发送。

Ported from: LiteNetLib/MergedPacket.cs, NetPeer.cs (Merge相关部分)
"""

import struct
import time
from typing import List, Optional
from litenetlib.core.packet import NetPacket
from litenetlib.core.constants import PacketProperty, NetConstants


class MergedPacket:
    """
    Merged packet manager / 合并包管理器

    Combines multiple small packets into one larger packet to reduce overhead.
    将多个小包合并成一个大包以减少开销。
    """

    def __init__(self, max_size: int = NetConstants.MAX_PACKET_SIZE):
        """
        Initialize merged packet / 初始化合并包

        Args:
            max_size: Maximum size of merged packet / 合并包最大大小
        """
        self._max_size = max_size
        self._packets: List[NetPacket] = []
        self._total_size = 0
        self._merge_timer = 0.0
        self._merge_delay = 0.010  # 10ms merge delay

    @property
    def packet_count(self) -> int:
        """Get number of packets in merge buffer / 获取合并缓冲区中的包数量"""
        return len(self._packets)

    @property
    def can_merge(self) -> bool:
        """Check if can add more packets / 检查是否可以添加更多包"""
        return len(self._packets) < 255  # Max 255 packets

    @property
    def should_send(self) -> bool:
        """
        Check if merged packet should be sent / 检查是否应该发送合并包

        Returns:
            True if buffer is full or timeout / 缓冲区满或超时返回 True

        C# Reference: NetPeer.Update (merge logic)
        """
        # Check if buffer is full
        if len(self._packets) >= 255:
            return True

        # Check timeout
        # C#: if (_mergeTime != 0 && currentTime > _mergeTime + _mergeDelay)
        if self._merge_timer > 0 and time.time() > self._merge_timer + self._merge_delay:
            return True

        return False

    def add_packet(self, packet: NetPacket, current_time: float = 0.0) -> bool:
        """
        Add packet to merge buffer / 添加包到合并缓冲区

        Args:
            packet: Packet to merge / 要合并的包
            current_time: Current time in seconds / 当前时间（秒）

        Returns:
            True if packet added, False if buffer full / 添加成功返回 True

        C# Reference: NetPeer.TryMergePacket
        """
        # Check buffer space
        # C#: if (_packetsToMerge.Count >= 255)
        if not self.can_merge:
            return False

        # Calculate space needed
        # Each packet needs: 2 bytes for length + packet data
        # C#: int newSize = _mergeSize + packet.Size + sizeof(ushort)
        space_needed = self._total_size + 2 + packet.size

        # C#: if (newSize > NetConstants.MaxPacketSize)
        if space_needed > self._max_size:
            return False

        # Add packet
        # C#: _packetsToMerge.Add(packet);
        self._packets.append(packet)
        self._total_size = space_needed

        # Set timer on first packet
        # C#: if (_packetsToMerge.Count == 1)
        if len(self._packets) == 1:
            self._merge_timer = current_time

        return True

    def create_merged_packet(self) -> Optional[NetPacket]:
        """
        Create merged packet from buffer / 从缓冲区创建合并包

        Returns:
            Merged packet or None if buffer empty / 合并包或 None

        C# Reference: NetPeer.SendMerged
        """
        if not self._packets:
            return None

        # Calculate total size
        # C#: int mergedSize = sizeof(ushort) + _mergeSize;
        header_size = 2  # Packet count (ushort)

        # Create merged packet
        # C#: var mergedPacket = new NetPacket(PacketProperty.Merged, mergedSize);
        # mergedSize includes: packet count (ushort) + total packet data
        # Note: NetPacket size includes property byte, so we need 1 + 2 + self._total_size
        merged = NetPacket(PacketProperty.MERGED, 2 + self._total_size)
        # Note: Merged packets don't use fragmented flag

        # Write packet count (starting after property byte at offset 1)
        # C#: FastBitConverter.GetBytes((ushort)_packetsToMerge.Count, mergedPacket.RawData, 0);
        # In C#, the offset is relative to RawData, which includes the property byte
        merged._data[1:3] = struct.pack('<H', len(self._packets))

        # Write packets (offset starts after property + count)
        # C#: int offset = sizeof(ushort);
        offset = 3

        # C#: foreach (var p in _packetsToMerge)
        for packet in self._packets:
            # Write packet size
            packet_size = packet.size
            merged._data[offset:offset + 2] = struct.pack('<H', packet_size)
            offset += 2

            # Write packet data
            packet_data = packet.get_bytes()
            merged._data[offset:offset + len(packet_data)] = packet_data
            offset += len(packet_data)

        # Clear buffer
        self._packets.clear()
        self._total_size = 0
        self._merge_timer = 0.0

        return merged

    def clear(self) -> None:
        """Clear merge buffer / 清空合并缓冲区"""
        self._packets.clear()
        self._total_size = 0
        self._merge_timer = 0.0


def process_merged_packet(packet: NetPacket) -> List[NetPacket]:
    """
    Process merged packet and extract individual packets / 处理合并包并提取单独的包

    Args:
        packet: Merged packet / 合并包

    Returns:
        List of extracted packets / 提取的包列表

    C# Reference: NetPeer.ProcessPacket (MERGED handling)
    """
    packets = []

    # Read packet count (starting after property byte at offset 1)
    # C#: ushort count = FastBitConverter.ToUInt16(packet.RawData, 0);
    # In C#, the offset is relative to RawData, which includes the property byte
    count = struct.unpack('<H', packet._data[1:3])[0]

    # C#: int offset = sizeof(ushort);
    # Offset starts after property byte + packet count
    offset = 3

    # Extract packets
    # C#: for (int i = 0; i < count; i++)
    for _ in range(count):
        # Read packet size
        # C#: ushort size = FastBitConverter.ToUInt16(packet.RawData, offset);
        size = struct.unpack('<H', packet._data[offset:offset + 2])[0]
        offset += 2

        # Read packet data
        # C#: var p = NetPacket.Deserialize(packet.RawData, offset, size, out readSize);
        packet_data = packet._data[offset:offset + size]
        offset += size

        # Create packet from data
        # C#: _packets.Add(p);
        extracted_packet = NetPacket.from_bytes(packet_data)
        packets.append(extracted_packet)

    return packets
