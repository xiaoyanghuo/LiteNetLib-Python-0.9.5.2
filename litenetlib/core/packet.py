"""
Network packet implementation / 网络数据包实现

Packets are the fundamental unit of data transfer in LiteNetLib.
Each packet has a header containing metadata and optional payload data.

数据包是 LiteNetLib 中数据传输的基本单位。
每个数据包都有包含元数据的头部和可选的负载数据。

Ported from: LiteNetLib/NetPacket.cs (v0.9.5.2)
"""

from typing import Optional
from litenetlib.core.constants import PacketProperty, NetConstants, get_header_size
from litenetlib.utils.fast_bit_converter import FastBitConverter


class NetPacket:
    """
    Represents a network packet with header and data.
    表示具有头部和数据的网络数据包。

    Header structure (first byte) / 头部结构（第一个字节）:
    - Bits 0-4: PacketProperty (5 bits, values 0-31) / 数据包属性
    - Bits 5-6: ConnectionNumber (2 bits, values 0-3) / 连接编号
    - Bit 7: Fragmented flag (1 bit) / 分片标志

    For channeled packets, additional header / 对于通道数据包，额外的头部:
    - Bytes 1-2: Sequence number (ushort) / 序列号
    - Byte 3: Channel ID / 通道 ID

    For fragmented packets / 对于分片数据包:
    - Bytes 4-5: Fragment ID (ushort) / 分片 ID
    - Bytes 6-7: Fragment Part (ushort) / 分片部分
    - Bytes 8-9: Fragments Total (ushort) / 分片总数

    C# Reference: NetPacket.cs
    """

    # Pre-calculated header sizes for each packet property / 每种数据包属性的预计算头部大小
    _header_sizes = {
        prop: get_header_size(prop) for prop in PacketProperty
    }

    __slots__ = ('_data', '_size', '_user_data')

    def __init__(self, size_or_property, property_or_size=None, size=None):
        """
        Create a new NetPacket / 创建新的 NetPacket。

        Args:
            size_or_property: Either packet size in bytes, or a PacketProperty
                            可以是数据包大小（字节）或 PacketProperty
            property_or_size: If first arg is size, this is PacketProperty
                            如果第一个参数是大小，则是 PacketProperty
            size: Data size (only when creating with property)
                 数据大小（仅在用属性创建时）
        """
        # Check if it's a PacketProperty (IntEnum values are int, need special check)
        # 检查是否为 PacketProperty（IntEnum 值是 int，需要特殊检查）
        try:
            # Try to convert to PacketProperty - if successful and second arg is int, it's a property
            # 尝试转换为 PacketProperty - 如果成功且第二个参数是 int，则是属性
            prop = PacketProperty(size_or_property)
            # If second arg is an int (data size), treat first arg as property
            # 如果第二个参数是 int（数据大小），则将第一个参数视为属性
            if property_or_size is None or isinstance(property_or_size, int):
                data_size = property_or_size if property_or_size is not None else 0
                header_size = NetPacket._header_sizes[prop]
                self._data = bytearray(header_size + data_size)
                self._size = len(self._data)
                self._user_data = None
                # Set packet property in the first byte / 在第一个字节中设置数据包属性
                self._data[0] = prop & 0x1F
                return
        except (ValueError, KeyError):
            # Not a valid PacketProperty, treat as size
            # 不是有效的 PacketProperty，视为大小
            pass

        # Create with size / 使用大小创建
        self._data = bytearray(size_or_property)
        self._size = size_or_property
        self._user_data = None

    @classmethod
    def from_bytes(cls, data: bytes) -> 'NetPacket':
        """
        Create a packet from existing bytes / 从现有字节创建数据包。

        Args:
            data: Source bytes / 源字节

        Returns:
            NetPacket instance / NetPacket 实例
        """
        packet = cls(len(data))
        packet._data[:] = data
        packet._size = len(data)
        return packet

    @property
    def packet_property(self) -> PacketProperty:
        """
        Get packet property type / 获取数据包属性类型。

        C#: Property { get { return (PacketProperty)(RawData[0] & 0x1F); } }
        """
        return PacketProperty(self._data[0] & 0x1F)

    @packet_property.setter
    def packet_property(self, value: PacketProperty) -> None:
        """
        Set packet property type / 设置数据包属性类型。

        C#: Property { set { RawData[0] = (byte)((RawData[0] & 0xE0) | (byte)value); } }
        """
        self._data[0] = (self._data[0] & 0xE0) | (value & 0x1F)

    @property
    def connection_number(self) -> int:
        """
        Get connection number (0-3) / 获取连接编号（0-3）。

        C#: ConnectionNumber { get { return (byte)((RawData[0] & 0x60) >> 5); } }
        """
        return (self._data[0] & 0x60) >> 5

    @connection_number.setter
    def connection_number(self, value: int) -> None:
        """
        Set connection number (0-3) / 设置连接编号（0-3）。

        C#: ConnectionNumber { set { RawData[0] = (byte) ((RawData[0] & 0x9F) | (value << 5)); } }
        """
        self._data[0] = (self._data[0] & 0x9F) | ((value & 0x03) << 5)

    @property
    def sequence(self) -> int:
        """
        Get sequence number (ushort, little-endian) / 获取序列号（ushort，小端序）。

        C#: Sequence { get { return BitConverter.ToUInt16(RawData, 1); } }
        """
        return (self._data[1] & 0xFF) | ((self._data[2] & 0xFF) << 8)

    @sequence.setter
    def sequence(self, value: int) -> None:
        """
        Set sequence number (ushort, little-endian) / 设置序列号（ushort，小端序）。

        Value is automatically masked to ushort range (0-65535) to handle wraparound.
        值会自动被屏蔽到 ushort 范围（0-65535）以处理回绕。

        C#: Sequence { set { FastBitConverter.GetBytes(RawData, 1, value); } }
        """
        # Mask to ushort range to handle wraparound (C# implicitly does this)
        value = value & 0xFFFF
        FastBitConverter.get_bytes_ushort(self._data, 1, value)

    @property
    def is_fragmented(self) -> bool:
        """
        Check if packet is fragmented / 检查数据包是否分片。

        C#: IsFragmented { get { return (RawData[0] & 0x80) != 0; } }
        """
        return (self._data[0] & 0x80) != 0

    def mark_fragmented(self) -> None:
        """
        Mark packet as fragmented / 标记数据包为分片。

        C#: MarkFragmented() { RawData[0] |= 0x80; }
        """
        self._data[0] |= 0x80

    @property
    def channel_id(self) -> int:
        """
        Get channel ID / 获取通道 ID。

        C#: ChannelId { get { return RawData[3]; } }
        """
        return self._data[3]

    @channel_id.setter
    def channel_id(self, value: int) -> None:
        """
        Set channel ID / 设置通道 ID。

        C#: ChannelId { set { RawData[3] = value; } }
        """
        self._data[3] = value & 0xFF

    @property
    def fragment_id(self) -> int:
        """
        Get fragment ID (ushort, little-endian, at offset 4) / 获取分片 ID。

        C#: FragmentId { get { return BitConverter.ToUInt16(RawData, 4); } }
        """
        return (self._data[4] & 0xFF) | ((self._data[5] & 0xFF) << 8)

    @fragment_id.setter
    def fragment_id(self, value: int) -> None:
        """
        Set fragment ID (ushort, little-endian, at offset 4) / 设置分片 ID。

        Auto-expands buffer if needed for fragmentation attributes.
        如果需要，自动扩展缓冲区以容纳分片属性。

        C#: FragmentId { set { FastBitConverter.GetBytes(RawData, 4, value); } }
        """
        # Ensure buffer is large enough for fragmentation data
        min_size = 10  # 4 (channeled header) + 6 (fragment header)
        if len(self._data) < min_size:
            # Expand buffer to accommodate fragmentation
            new_data = bytearray(min_size)
            new_data[:len(self._data)] = self._data
            self._data = new_data
            self._size = max(self._size, min_size)
        FastBitConverter.get_bytes_ushort(self._data, 4, value)

    @property
    def fragment_part(self) -> int:
        """
        Get fragment part number (ushort, little-endian, at offset 6) / 获取分片部分编号。

        C#: FragmentPart { get { return BitConverter.ToUInt16(RawData, 6); } }
        """
        return (self._data[6] & 0xFF) | ((self._data[7] & 0xFF) << 8)

    @fragment_part.setter
    def fragment_part(self, value: int) -> None:
        """
        Set fragment part number (ushort, little-endian, at offset 6) / 设置分片部分编号。

        Auto-expands buffer if needed for fragmentation attributes.
        如果需要，自动扩展缓冲区以容纳分片属性。

        C#: FragmentPart { set { FastBitConverter.GetBytes(RawData, 6, value); } }
        """
        # Ensure buffer is large enough for fragmentation data
        min_size = 10  # 4 (channeled header) + 6 (fragment header)
        if len(self._data) < min_size:
            # Expand buffer to accommodate fragmentation
            new_data = bytearray(min_size)
            new_data[:len(self._data)] = self._data
            self._data = new_data
            self._size = max(self._size, min_size)
        FastBitConverter.get_bytes_ushort(self._data, 6, value)

    @property
    def fragments_total(self) -> int:
        """
        Get total number of fragments (ushort, little-endian, at offset 8) / 获取分片总数。

        C#: FragmentsTotal { get { return BitConverter.ToUInt16(RawData, 8); } }
        """
        return (self._data[8] & 0xFF) | ((self._data[9] & 0xFF) << 8)

    @fragments_total.setter
    def fragments_total(self, value: int) -> None:
        """
        Set total number of fragments (ushort, little-endian, at offset 8) / 设置分片总数。

        Auto-expands buffer if needed for fragmentation attributes.
        如果需要，自动扩展缓冲区以容纳分片属性。

        C#: FragmentsTotal { set { FastBitConverter.GetBytes(RawData, 8, value); } }
        """
        # Ensure buffer is large enough for fragmentation data
        min_size = 10  # 4 (channeled header) + 6 (fragment header)
        if len(self._data) < min_size:
            # Expand buffer to accommodate fragmentation
            new_data = bytearray(min_size)
            new_data[:len(self._data)] = self._data
            self._data = new_data
            self._size = max(self._size, min_size)
        FastBitConverter.get_bytes_ushort(self._data, 8, value)

    @property
    def raw_data(self) -> memoryview:
        """
        Get raw packet data as memoryview for efficient access / 获取原始数据包数据。

        C#: RawData (public byte[])
        """
        return memoryview(self._data)[:self._size]

    @property
    def size(self) -> int:
        """
        Get packet size in bytes / 获取数据包大小（字节）。

        C#: Size (public int)
        """
        return self._size

    @size.setter
    def size(self, value: int) -> None:
        """
        Set packet size / 设置数据包大小。

        C#: Size (can be set to truncate packet)
        """
        self._size = min(value, len(self._data))

    @property
    def user_data(self) -> Optional[object]:
        """
        Get user-defined data attached to this packet / 获取附加到此数据包的用户定义数据。

        C#: UserData (public object)
        """
        return self._user_data

    @user_data.setter
    def user_data(self, value: Optional[object]) -> None:
        """
        Set user-defined data attached to this packet / 设置附加到此数据包的用户定义数据。

        C#: UserData (public object)
        """
        self._user_data = value

    def get_header_size(self) -> int:
        """
        Get header size for this packet's property type / 获取此数据包属性类型的头部大小。

        C#: GetHeaderSize() { return HeaderSizes[RawData[0] & 0x1F]; }

        Returns:
            Header size in bytes / 头部大小（字节）
        """
        return self._header_sizes[self.packet_property]

    def get_data(self) -> bytes:
        """
        Get packet data (excluding header) / 获取数据包数据（不包括头部）。

        Returns:
            Packet payload data / 数据包负载数据
        """
        header_size = self.get_header_size()
        return bytes(self._data[header_size:self._size])

    def get_bytes(self) -> bytes:
        """
        Get complete packet as bytes / 获取完整数据包的字节。

        Returns:
            Complete packet including header / 包括头部的完整数据包
        """
        return bytes(self._data[:self._size])

    def verify(self) -> bool:
        """
        Verify packet is valid / 验证数据包是否有效。

        C#: Verify() implementation

        Returns:
            True if packet has valid structure, False otherwise.
            如果数据包结构有效则返回 True，否则返回 False。
        """
        prop = self._data[0] & 0x1F
        if prop >= len(PacketProperty):
            return False

        try:
            prop_enum = PacketProperty(prop)
        except ValueError:
            return False

        header_size = self._header_sizes.get(prop_enum, NetConstants.HEADER_SIZE)
        if self._size < header_size:
            return False

        # C#: if (fragmented || Size >= headerSize + FragmentHeaderSize)
        if self.is_fragmented and self._size < header_size + NetConstants.FRAGMENT_HEADER_SIZE:
            return False

        return True

    def __len__(self) -> int:
        """Get packet size / 获取数据包大小"""
        return self._size

    def __bytes__(self) -> bytes:
        """Convert to bytes / 转换为字节"""
        return self.get_bytes()

    def __repr__(self) -> str:
        """String representation / 字符串表示"""
        return (f"NetPacket(packet_property={self.packet_property.name}, "
                f"size={self._size}, fragmented={self.is_fragmented})")


class NetPacketPool:
    """
    Simple object pool for NetPacket instances to reduce allocations.
    NetPacket 对象池，用于减少分配。

    In Python, the GC handles memory well, but pooling can still help
    reduce allocation overhead for high-throughput scenarios.

    在 Python 中，GC 可以很好地处理内存，但池化仍然可以帮助
    减少高吞吐量场景的分配开销。

    C# Reference: NetPacketPool.cs
    """

    __slots__ = ('_pool', '_max_size')

    def __init__(self, max_size: int = NetConstants.PACKET_POOL_SIZE):
        """
        Create packet pool / 创建数据包池。

        Args:
            max_size: Maximum pool size / 最大池大小
        """
        self._pool = []
        self._max_size = max_size

    def get(self, size: int) -> NetPacket:
        """
        Get a packet from the pool or create a new one / 从池中获取或创建新数据包。

        Args:
            size: Required minimum size / 需要的最小大小

        Returns:
            NetPacket instance / NetPacket 实例
        """
        if self._pool:
            packet = self._pool.pop()
            if len(packet._data) >= size:
                packet._size = size
                return packet
        return NetPacket(size)

    def recycle(self, packet: NetPacket) -> None:
        """
        Return a packet to the pool for reuse / 将数据包返回到池中以供重用。

        Args:
            packet: Packet to recycle / 要回收的数据包
        """
        if len(self._pool) < self._max_size:
            packet._user_data = None
            self._pool.append(packet)

    def clear(self) -> None:
        """Clear the pool / 清空池"""
        self._pool.clear()
