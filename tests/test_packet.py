"""
NetPacket Tests / 数据包测试

Tests for NetPacket class including creation, properties, fragmentation,
and packet verification.

Reference C# Code: LiteNetLib/NetPacket.cs
"""

import pytest
from litenetlib.core.packet import NetPacket, NetPacketPool
from litenetlib.core.constants import (
    PacketProperty,
    NetConstants,
    get_header_size
)


class TestNetPacketCreation:
    """Test NetPacket creation / 测试 NetPacket 创建"""

    def test_create_with_size(self):
        """Test creating packet with size / 测试使用大小创建数据包"""
        packet = NetPacket(100)
        assert packet.size == 100, f"Packet size should be 100, got {packet.size}"
        assert len(packet.raw_data) == 100, f"Raw data length should be 100, got {len(packet.raw_data)}"

    def test_create_with_property(self):
        """Test creating packet with property / 测试使用属性创建数据包"""
        packet = NetPacket(PacketProperty.UNRELIABLE, 50)
        assert packet.size == 51, f"Packet size should be 51 (1 header + 50 data), got {packet.size}"
        assert packet.packet_property == PacketProperty.UNRELIABLE, \
            f"Packet property should be UNRELIABLE, got {packet.packet_property}"

    def test_create_with_property_no_data(self):
        """Test creating packet with property but no data / 测试创建有属性但无数据的数据包"""
        packet = NetPacket(PacketProperty.CHANNELED)
        header_size = get_header_size(PacketProperty.CHANNELED)
        assert packet.size == header_size, \
            f"Packet size should be {header_size}, got {packet.size}"
        assert packet.packet_property == PacketProperty.CHANNELED

    def test_create_with_all_properties(self):
        """Test creating packets with all property types / 测试创建所有属性类型的数据包"""
        for prop in PacketProperty:
            packet = NetPacket(prop, 10)
            assert packet.packet_property == prop, \
                f"Packet property should be {prop}, got {packet.packet_property}"
            expected_size = get_header_size(prop) + 10
            assert packet.size == expected_size, \
                f"Packet size for {prop.name} should be {expected_size}, got {packet.size}"

    def test_from_bytes(self):
        """Test creating packet from bytes / 测试从字节创建数据包"""
        data = b'\x05Hello World'  # CONNECT_REQUEST + data
        packet = NetPacket.from_bytes(data)
        assert packet.size == len(data), f"Packet size should be {len(data)}, got {packet.size}"
        assert bytes(packet.raw_data) == data, "Raw data should match input"

    def test_invalid_creation_type(self):
        """Test invalid creation parameter type / 测试无效的创建参数类型"""
        with pytest.raises(TypeError):
            NetPacket("invalid")  # Should raise TypeError


class TestPacketProperty:
    """Test packet_property getter/setter / 测试 packet_property 获取器/设置器"""

    def test_get_packet_property(self):
        """Test getting packet property / 测试获取数据包属性"""
        packet = NetPacket(PacketProperty.CHANNELED, 0)
        assert packet.packet_property == PacketProperty.CHANNELED, \
            f"Property should be CHANNELED, got {packet.packet_property}"

    def test_set_packet_property(self):
        """Test setting packet property / 测试设置数据包属性"""
        packet = NetPacket(100)
        packet.packet_property = PacketProperty.UNRELIABLE
        assert packet.packet_property == PacketProperty.UNRELIABLE, \
            f"Property should be UNRELIABLE after set, got {packet.packet_property}"

    def test_packet_property_bits_masking(self):
        """Test packet property uses only lower 5 bits / 测试数据包属性仅使用低 5 位"""
        packet = NetPacket(100)
        packet.packet_property = PacketProperty.CHANNELED  # Value = 1

        # First byte should have property in lower 5 bits
        first_byte = packet.raw_data[0]
        assert (first_byte & 0x1F) == 1, \
            f"Lower 5 bits should contain property value (1), got {first_byte & 0x1F}"

    def test_set_all_packet_properties(self):
        """Test setting all packet property values / 测试设置所有数据包属性值"""
        packet = NetPacket(100)
        for prop in PacketProperty:
            packet.packet_property = prop
            assert packet.packet_property == prop, \
                f"Failed to set and get property {prop.name}"


class TestConnectionNumber:
    """Test connection_number getter/setter / 测试 connection_number 获取器/设置器"""

    def test_get_connection_number_default(self):
        """Test default connection number is 0 / 测试默认连接编号为 0"""
        packet = NetPacket(100)
        assert packet.connection_number == 0, \
            f"Default connection number should be 0, got {packet.connection_number}"

    def test_set_connection_number(self):
        """Test setting connection number / 测试设置连接编号"""
        packet = NetPacket(100)
        for i in range(4):  # Connection numbers are 0-3 (2 bits)
            packet.connection_number = i
            assert packet.connection_number == i, \
                f"Connection number should be {i}, got {packet.connection_number}"

    def test_connection_number_bits_masking(self):
        """Test connection number uses bits 5-6 / 测试连接编号使用第 5-6 位"""
        packet = NetPacket(100)
        packet.connection_number = 2

        # First byte should have connection number in bits 5-6
        first_byte = packet.raw_data[0]
        expected = (2 & 0x03) << 5  # Value shifted left by 5
        assert (first_byte & 0x60) == expected, \
            f"Bits 5-6 should contain connection number (2), got {(first_byte & 0x60) >> 5}"

    def test_connection_number_max_value(self):
        """Test connection number maximum value is 3 / 测试连接编号最大值为 3"""
        packet = NetPacket(100)
        packet.connection_number = 3
        assert packet.connection_number == 3

        # Value 4 should be masked to 0 (only 2 bits)
        packet.connection_number = 4
        assert packet.connection_number == 0, \
            f"Connection number 4 should be masked to 0, got {packet.connection_number}"

    def test_connection_number_with_property(self):
        """Test connection number and property don't interfere / 测试连接编号和属性不冲突"""
        packet = NetPacket(100)
        packet.packet_property = PacketProperty.CHANNELED  # Value 1
        packet.connection_number = 2

        assert packet.packet_property == PacketProperty.CHANNELED
        assert packet.connection_number == 2


class TestSequence:
    """Test sequence getter/setter / 测试 sequence 获取器/设置器"""

    def test_get_sequence_default(self):
        """Test default sequence is 0 / 测试默认序列号为 0"""
        packet = NetPacket(PacketProperty.CHANNELED, 0)
        assert packet.sequence == 0, \
            f"Default sequence should be 0, got {packet.sequence}"

    def test_set_sequence(self):
        """Test setting sequence / 测试设置序列号"""
        packet = NetPacket(PacketProperty.CHANNELED, 0)
        packet.sequence = 1000
        assert packet.sequence == 1000, \
            f"Sequence should be 1000, got {packet.sequence}"

    def test_sequence_little_endian(self):
        """Test sequence is stored in little-endian / 测试序列号以小端存储"""
        packet = NetPacket(PacketProperty.CHANNELED, 0)
        packet.sequence = 0x1234

        # Bytes 1-2 should contain little-endian representation
        byte1 = packet.raw_data[1]
        byte2 = packet.raw_data[2]
        assert byte1 == 0x34, f"Byte 1 should be 0x34, got 0x{byte1:02X}"
        assert byte2 == 0x12, f"Byte 2 should be 0x12, got 0x{byte2:02X}"

    def test_sequence_max_value(self):
        """Test sequence max value (ushort) / 测试序列号最大值"""
        packet = NetPacket(PacketProperty.CHANNELED, 0)
        packet.sequence = 65535  # Max ushort
        assert packet.sequence == 65535

    def test_sequence_wraparound(self):
        """Test sequence wraparound / 测试序列号循环"""
        packet = NetPacket(PacketProperty.CHANNELED, 0)
        packet.sequence = 65536  # Should wrap to 0
        assert packet.sequence == 0, \
            f"Sequence 65536 should wrap to 0, got {packet.sequence}"


class TestChannelId:
    """Test channel_id getter/setter / 测试 channel_id 获取器/设置器"""

    def test_get_channel_id_default(self):
        """Test default channel_id is 0 / 测试默认 channel_id 为 0"""
        packet = NetPacket(PacketProperty.CHANNELED, 0)
        assert packet.channel_id == 0, \
            f"Default channel_id should be 0, got {packet.channel_id}"

    def test_set_channel_id(self):
        """Test setting channel_id / 测试设置 channel_id"""
        packet = NetPacket(PacketProperty.CHANNELED, 0)
        packet.channel_id = 5
        assert packet.channel_id == 5, \
            f"channel_id should be 5, got {packet.channel_id}"

    def test_channel_id_byte_position(self):
        """Test channel_id is at byte 3 / 测试 channel_id 在第 3 字节"""
        packet = NetPacket(PacketProperty.CHANNELED, 0)
        packet.channel_id = 42
        assert packet.raw_data[3] == 42, \
            f"Byte 3 should be 42, got {packet.raw_data[3]}"


class TestFragmentation:
    """Test fragmentation flags and properties / 测试分片标志和属性"""

    def test_is_fragmented_default(self):
        """Test default is_fragmented is False / 测试默认 is_fragmented 为 False"""
        packet = NetPacket(PacketProperty.CHANNELED, 0)
        assert not packet.is_fragmented, \
            f"Default is_fragmented should be False, got {packet.is_fragmented}"

    def test_mark_fragmented(self):
        """Test marking packet as fragmented / 测试标记数据包为分片"""
        packet = NetPacket(PacketProperty.CHANNELED, 0)
        packet.mark_fragmented()
        assert packet.is_fragmented, \
            f"is_fragmented should be True after mark_fragmented(), got {packet.is_fragmented}"

    def test_fragmented_bit_position(self):
        """Test fragmented flag is bit 7 / 测试分片标志在第 7 位"""
        packet = NetPacket(100)
        packet.mark_fragmented()

        first_byte = packet.raw_data[0]
        assert (first_byte & 0x80) != 0, \
            f"Bit 7 should be set for fragmented packet, got {first_byte:02X}"

    def test_fragment_id(self):
        """Test fragment_id / 测试 fragment_id"""
        packet = NetPacket(PacketProperty.CHANNELED, 0)
        packet.fragment_id = 123
        assert packet.fragment_id == 123, \
            f"fragment_id should be 123, got {packet.fragment_id}"

    def test_fragment_part(self):
        """Test fragment_part / 测试 fragment_part"""
        packet = NetPacket(PacketProperty.CHANNELED, 0)
        packet.fragment_part = 5
        assert packet.fragment_part == 5, \
            f"fragment_part should be 5, got {packet.fragment_part}"

    def test_fragments_total(self):
        """Test fragments_total / 测试 fragments_total"""
        packet = NetPacket(PacketProperty.CHANNELED, 0)
        packet.fragments_total = 10
        assert packet.fragments_total == 10, \
            f"fragments_total should be 10, got {packet.fragments_total}"

    def test_fragment_properties_little_endian(self):
        """Test fragment properties are little-endian / 测试分片属性为小端序"""
        packet = NetPacket(PacketProperty.CHANNELED, 0)
        packet.fragment_id = 0x1234
        packet.fragment_part = 0x5678
        packet.fragments_total = 0x9ABC

        # Check byte positions (4-9 for fragment data)
        assert packet.raw_data[4] == 0x34  # fragment_id low byte
        assert packet.raw_data[5] == 0x12  # fragment_id high byte
        assert packet.raw_data[6] == 0x78  # fragment_part low byte
        assert packet.raw_data[7] == 0x56  # fragment_part high byte
        assert packet.raw_data[8] == 0xBC  # fragments_total low byte
        assert packet.raw_data[9] == 0x9A  # fragments_total high byte


class TestPacketData:
    """Test packet data access / 测试数据包数据访问"""

    def test_get_data_empty(self):
        """Test getting data from packet with no payload / 测试从无负载数据包获取数据"""
        packet = NetPacket(PacketProperty.UNRELIABLE, 0)
        data = packet.get_data()
        assert data == b'', f"Data should be empty, got {data!r}"

    def test_get_data_with_payload(self):
        """Test getting data from packet with payload / 测试从有负载数据包获取数据"""
        # Create packet and manually add data
        packet = NetPacket(PacketProperty.UNRELIABLE, 10)
        # Add some data after header
        packet._data[1:11] = b'0123456789'
        packet._size = 11

        data = packet.get_data()
        assert data == b'0123456789', f"Data should be '0123456789', got {data!r}"

    def test_get_bytes(self):
        """Test get_bytes returns complete packet / 测试 get_bytes 返回完整数据包"""
        packet = NetPacket(PacketProperty.UNRELIABLE, 5)
        packet._data[1:6] = b'HELLO'

        bytes_data = packet.get_bytes()
        assert len(bytes_data) == packet.size
        assert bytes_data[0] == PacketProperty.UNRELIABLE

    def test_size_property(self):
        """Test size property / 测试 size 属性"""
        packet = NetPacket(100)
        assert packet.size == 100

        packet.size = 50
        assert packet.size == 50, \
            f"Size should be 50 after setting, got {packet.size}"

    def test_size_truncation(self):
        """Test size truncates to buffer length / 测试大小截断为缓冲区长度"""
        packet = NetPacket(100)
        packet.size = 200  # Try to set larger than buffer
        assert packet.size == 100, \
            f"Size should be truncated to buffer length (100), got {packet.size}"


class TestPacketVerification:
    """Test packet verification / 测试数据包验证"""

    def test_verify_valid_packet(self):
        """Test verifying valid packet / 测试验证有效数据包"""
        packet = NetPacket(PacketProperty.UNRELIABLE, 10)
        assert packet.verify(), "Valid packet should pass verification"

    def test_verify_all_property_types(self):
        """Test verifying all property types / 测试验证所有属性类型"""
        for prop in PacketProperty:
            packet = NetPacket(prop, 10)
            assert packet.verify(), f"Packet with property {prop.name} should be valid"

    def test_verify_invalid_size(self):
        """Test verifying packet with invalid size / 测试验证无效大小的数据包"""
        packet = NetPacket(PacketProperty.CHANNELED, 0)
        packet._size = 2  # Smaller than header size (4)
        assert not packet.verify(), \
            "Packet with size smaller than header should fail verification"

    def test_verify_fragmented_without_size(self):
        """Test verifying fragmented packet without enough size / 测试验证没有足够大小的分片数据包"""
        packet = NetPacket(PacketProperty.CHANNELED, 0)
        packet.mark_fragmented()
        packet._size = 5  # Header (4) but no room for fragment header (6)
        assert not packet.verify(), \
            "Fragmented packet without fragment header size should fail verification"

    def test_verify_fragmented_with_proper_size(self):
        """Test verifying fragmented packet with proper size / 测试验证有正确大小的分片数据包"""
        # Create a packet large enough for fragmentation (header + fragment header = 10 bytes)
        packet = NetPacket(PacketProperty.CHANNELED, 10)  # 10 bytes minimum for fragmented
        packet.mark_fragmented()
        # Should have room for header (4) + fragment header (6) = 10
        assert packet.verify(), \
            "Fragmented packet with proper size should pass verification"


class TestPacketPool:
    """Test NetPacketPool / 测试 NetPacketPool"""

    def test_pool_creation(self):
        """Test creating packet pool / 测试创建数据包池"""
        pool = NetPacketPool()
        assert pool is not None, "Pool should be created"

    def test_pool_get_packet(self):
        """Test getting packet from pool / 测试从池获取数据包"""
        pool = NetPacketPool()
        packet = pool.get(100)
        assert packet is not None, "Should get packet from pool"
        assert packet.size == 100, f"Packet size should be 100, got {packet.size}"

    def test_pool_recycle_packet(self):
        """Test recycling packet to pool / 测试回收数据包到池"""
        pool = NetPacketPool()
        packet = pool.get(100)
        packet.user_data = "test"
        pool.recycle(packet)

        # User data should be cleared
        assert packet.user_data is None, \
            "User data should be cleared after recycle"

    def test_pool_reuse_packet(self):
        """Test reusing packet from pool / 测试重用池中的数据包"""
        pool = NetPacketPool()
        packet1 = pool.get(100)
        pool.recycle(packet1)

        packet2 = pool.get(50)
        # Should reuse packet1 if size is sufficient
        assert packet2.size == 50

    def test_pool_clear(self):
        """Test clearing pool / 测试清空池"""
        pool = NetPacketPool()
        pool.get(100)
        pool.get(200)
        pool.clear()

        # Pool should be empty, next get creates new packet
        packet = pool.get(100)
        assert packet is not None

    def test_pool_max_size(self):
        """Test pool max size limit / 测试池最大大小限制"""
        pool = NetPacketPool(max_size=5)

        # Add more packets than max size
        for i in range(10):
            packet = pool.get(100)
            pool.recycle(packet)

        # Pool should not exceed max size
        assert len(pool._pool) <= 5, \
            f"Pool size should not exceed max_size (5), got {len(pool._pool)}"


class TestPacketConversions:
    """Test packet conversions / 测试数据包转换"""

    def test_len(self):
        """Test __len__ returns size / 测试 __len__ 返回大小"""
        packet = NetPacket(100)
        assert len(packet) == 100

    def test_bytes_conversion(self):
        """Test __bytes__ conversion / 测试 __bytes__ 转换"""
        packet = NetPacket(PacketProperty.UNRELIABLE, 5)
        packet._data[1:6] = b'HELLO'

        packet_bytes = bytes(packet)
        assert isinstance(packet_bytes, bytes)
        assert len(packet_bytes) == packet.size

    def test_repr(self):
        """Test __repr__ string representation / 测试 __repr__ 字符串表示"""
        packet = NetPacket(PacketProperty.CHANNELED, 50)
        repr_str = repr(packet)

        assert 'NetPacket' in repr_str
        assert 'CHANNELED' in repr_str
        assert 'size=' in repr_str


class TestUserData:
    """Test user_data property / 测试 user_data 属性"""

    def test_user_data_default(self):
        """Test default user_data is None / 测试默认 user_data 为 None"""
        packet = NetPacket(100)
        assert packet.user_data is None

    def test_set_user_data(self):
        """Test setting user_data / 测试设置 user_data"""
        packet = NetPacket(100)
        packet.user_data = "test data"
        assert packet.user_data == "test data"

    def test_user_data_object(self):
        """Test user_data with arbitrary object / 测试 user_data 为任意对象"""
        packet = NetPacket(100)
        obj = {"key": "value", "number": 42}
        packet.user_data = obj
        assert packet.user_data == obj

    def test_clear_user_data(self):
        """Test clearing user_data / 测试清除 user_data"""
        packet = NetPacket(100)
        packet.user_data = "data"
        packet.user_data = None
        assert packet.user_data is None


class TestPacketRawData:
    """Test raw_data property / 测试 raw_data 属性"""

    def test_raw_data_type(self):
        """Test raw_data returns memoryview / 测试 raw_data 返回 memoryview"""
        packet = NetPacket(100)
        raw = packet.raw_data
        assert isinstance(raw, memoryview), \
            f"raw_data should be memoryview, got {type(raw)}"

    def test_raw_data_modification(self):
        """Test raw_data can be modified / 测试 raw_data 可被修改"""
        packet = NetPacket(100)
        packet.raw_data[0] = 42
        assert packet._data[0] == 42

    def test_raw_data_size(self):
        """Test raw_data respects size / 测试 raw_data 遵循 size"""
        packet = NetPacket(100)
        packet._size = 50
        raw = packet.raw_data
        assert len(raw) == 50, \
            f"raw_data length should match size (50), got {len(raw)}"


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
