"""
Fragment handling for large packets.

Implements packet fragmentation and reassembly for packets larger than MTU.

Ported from: LiteNetLib/NetPeer.cs (Fragmentation相关部分)
"""

import struct
import time
from typing import Optional, List, Dict
from litenetlib.core.packet import NetPacket
from litenetlib.core.constants import NetConstants, PacketProperty


class IncomingFragment:
    """
    Represents a fragment group being assembled.

    Stores received fragments until all fragments of a group arrive.
    """

    __slots__ = ('_fragments', '_fragment_count', '_first_fragment', '_timestamp', '_total_size')

    def __init__(self, fragment_count: int, total_size: int):
        """
        Initialize fragment group.

        Args:
            fragment_count: Total number of fragments / 总分片数
            total_size: Total size of reassembled data / 重组后的总大小
        """
        self._fragment_count = fragment_count
        self._total_size = total_size
        self._fragments: List[Optional[bytes]] = [None] * fragment_count
        self._first_fragment: Optional[NetPacket] = None
        self._timestamp = time.time()

    @property
    def age(self) -> float:
        """Get age of fragment group in seconds / 获取分片组的年龄（秒）"""
        return time.time() - self._timestamp

    def add_fragment(self, fragment_id: int, data: bytes) -> bool:
        """
        Add a fragment to the group.

        Args:
            fragment_id: Fragment number (0-based) / 分片编号（从0开始）
            data: Fragment data / 分片数据

        Returns:
            True if fragment was added, False if duplicate / 是否添加成功
        """
        if self._fragments[fragment_id] is not None:
            return False  # Duplicate fragment / 重复分片
        self._fragments[fragment_id] = data
        return True

    def set_first_fragment(self, packet: NetPacket) -> None:
        """Set the first fragment (contains header) / 设置第一个分片（包含头部）"""
        self._first_fragment = packet

    def is_complete(self) -> bool:
        """Check if all fragments have arrived / 检查是否所有分片都已到达"""
        return all(f is not None for f in self._fragments)

    def assemble(self) -> Optional[NetPacket]:
        """
        Assemble all fragments into a single packet.

        Returns:
            Reassembled packet or None if incomplete / 重组后的数据包或None

        C# Reference: NetPeer.ProcessPacket
        """
        if not self.is_complete():
            return None

        # Combine all fragments
        # C#: byte[] data = new byte[_totalSize];
        #     Buffer.BlockCopy(_firstFragment.RawData, 0, data, 0, _firstFragment.Size);
        #     int currentOffset = _firstFragment.Size;
        #     ...
        data = bytearray(self._total_size)

        # Copy first fragment
        if self._first_fragment:
            first_data = self._first_fragment.get_data()
            offset = len(first_data)
            data[:offset] = first_data

            # Copy remaining fragments
            for i, fragment_data in enumerate(self._fragments):
                if i == 0:
                    continue  # Already copied first fragment
                if fragment_data:
                    data[offset:offset + len(fragment_data)] = fragment_data
                    offset += len(fragment_data)

        # Create new packet from assembled data
        # C#: var packet = new NetPacket(reader, DeliveryMethod.ReliableOrdered, 0);
        new_packet = NetPacket.from_bytes(bytes(data))
        return new_packet


class FragmentPool:
    """
    Manages incoming fragment groups.

    Handles fragment assembly, timeout, and cleanup.
    """

    def __init__(self, timeout: float = 5.0):
        """
        Initialize fragment pool.

        Args:
            timeout: Fragment group timeout in seconds / 分片组超时时间（秒）
        """
        self._fragments: Dict[int, IncomingFragment] = {}
        self._timeout = timeout

    def get_fragments(self, fragment_group_id: int) -> Optional[IncomingFragment]:
        """
        Get fragment group by ID.

        Args:
            fragment_group_id: Fragment group ID / 分片组ID

        Returns:
            Fragment group or None / 分片组或None
        """
        return self._fragments.get(fragment_group_id)

    def create_fragments(self, fragment_group_id: int, fragment_count: int, total_size: int) -> IncomingFragment:
        """
        Create a new fragment group.

        Args:
            fragment_group_id: Fragment group ID / 分片组ID
            fragment_count: Number of fragments / 分片数量
            total_size: Total size / 总大小

        Returns:
            New fragment group / 新分片组
        """
        fragments = IncomingFragment(fragment_count, total_size)
        self._fragments[fragment_group_id] = fragments
        return fragments

    def remove_fragments(self, fragment_group_id: int) -> None:
        """Remove fragment group / 移除分片组"""
        if fragment_group_id in self._fragments:
            del self._fragments[fragment_group_id]

    def cleanup_expired(self) -> int:
        """
        Remove expired fragment groups.

        Returns:
            Number of groups removed / 移除的组数

        C# Reference: NetPeer.Update
        """
        current_time = time.time()
        expired_keys = [
            key for key, frag in self._fragments.items()
            if frag.age > self._timeout
        ]
        for key in expired_keys:
            del self._fragments[key]
        return len(expired_keys)

    def clear(self) -> None:
        """Clear all fragment groups / 清理所有分片组"""
        self._fragments.clear()


def create_fragment_packet(
    data: bytes,
    fragment_id: int,
    fragment_part: int,
    fragment_total: int,
    channel_id: int
) -> NetPacket:
    """
    Create a fragment packet.

    Args:
        data: Fragment data / 分片数据
        fragment_id: Fragment group ID / 分片组ID
        fragment_part: Current fragment number (0-based) / 当前分片编号
        fragment_total: Total number of fragments / 总分片数
        channel_id: Channel ID / 通道ID

    Returns:
        Fragment packet / 分片数据包

    C# Reference: NetPeer.SendFragment
    """
    # Calculate size: header + fragment data
    # C#: int headerSize = NetConstants.ChanneledHeaderSize + NetConstants.FragmentHeaderSize;
    #     var packet = NetManager.PoolRentWithProperty(PacketProperty.Channeled, size);
    header_size = NetConstants.CHANNELED_HEADER_SIZE + NetConstants.FRAGMENT_HEADER_SIZE
    packet = NetPacket(PacketProperty.CHANNELED, header_size + len(data))

    # Set channel ID
    # C#: packet.ChannelId = (byte)((_fragmentId * NetConstants.MaxChannelTypeCount) + channelId);
    packet.channel_id = channel_id

    # Set fragment flag
    # C#: packet.SetFragmented(true);
    packet.mark_fragmented()

    # Write fragment header
    # C#: FastBitConverter.GetBytes(packet.RawData, NetConstants.ChanneledHeaderSize, _fragmentId);
    #     FastBitConverter.GetBytes(packet.RawData, NetConstants.ChanneledHeaderSize + 2, _fragmentPart);
    #     FastBitConverter.GetBytes(packet.RawData, NetConstants.ChanneledHeaderSize + 4, _fragmentTotal);
    packet._data[NetConstants.CHANNELED_HEADER_SIZE:NetConstants.CHANNELED_HEADER_SIZE + 2] = struct.pack('<H', fragment_id)
    packet._data[NetConstants.CHANNELED_HEADER_SIZE + 2:NetConstants.CHANNELED_HEADER_SIZE + 4] = struct.pack('<H', fragment_part)
    packet._data[NetConstants.CHANNELED_HEADER_SIZE + 4:NetConstants.CHANNELED_HEADER_SIZE + 6] = struct.pack('<H', fragment_total)

    # Write fragment data
    # C#: Buffer.BlockCopy(data, 0, packet.RawData, headerSize, data.Length);
    packet._data[header_size:] = data

    return packet


def parse_fragment_header(packet: NetPacket) -> tuple:
    """
    Parse fragment header from packet.

    Args:
        packet: Fragment packet / 分片数据包

    Returns:
        Tuple of (fragment_id, fragment_part, fragment_total) / (分片组ID, 分片编号, 总分片数)

    C# Reference: NetPeer.ProcessPacket
    """
    # C#: ushort fragmentId = FastBitConverter.ToUInt16(packet.RawData, NetConstants.ChanneledHeaderSize);
    #     ushort fragmentPart = FastBitConverter.ToUInt16(packet.RawData, NetConstants.ChanneledHeaderSize + 2);
    #     ushort fragmentTotal = FastBitConverter.ToUInt16(packet.RawData, NetConstants.ChanneledHeaderSize + 4);
    offset = NetConstants.CHANNELED_HEADER_SIZE
    fragment_id = struct.unpack('<H', packet._data[offset:offset + 2])[0]
    fragment_part = struct.unpack('<H', packet._data[offset + 2:offset + 4])[0]
    fragment_total = struct.unpack('<H', packet._data[offset + 4:offset + 6])[0]
    return fragment_id, fragment_part, fragment_total
