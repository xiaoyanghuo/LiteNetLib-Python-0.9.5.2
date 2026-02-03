"""
Protocol Compatibility Tests / 协议兼容性测试

Tests for verifying binary protocol compatibility with C# LiteNetLib v0.9.5.2.
Ensures all packet formats, byte orders, and encodings match exactly.

These tests verify byte-level compatibility to ensure Python implementation
can interoperate with C# implementation.

Reference C# Code: LiteNetLib v0.9.5.2
"""

import pytest
import struct
from litenetlib.core.packet import NetPacket
from litenetlib.core.constants import (
    PacketProperty,
    DeliveryMethod,
    NetConstants,
    get_header_size
)
from litenetlib.utils.data_writer import NetDataWriter
from litenetlib.utils.data_reader import NetDataReader


class TestPacketHeaderFormat:
    """Test packet header format matches C# / 测试数据包头部格式与 C# 匹配"""

    def test_header_byte_structure_unreliable(self):
        """Test UNRELIABLE packet header byte / 测试 UNRELIABLE 数据包头部字节"""
        packet = NetPacket(PacketProperty.UNRELIABLE, 0)

        # First byte structure (C#): Property (bits 0-4) | ConnectionNumber (bits 5-6) | Fragmented (bit 7)
        first_byte = packet.raw_data[0]

        # Property should be in bits 0-4
        prop = first_byte & 0x1F
        assert prop == PacketProperty.UNRELIABLE, \
            f"Property in bits 0-4 should be {PacketProperty.UNRELIABLE}, got {prop}"

        # ConnectionNumber should be 0 in bits 5-6
        conn_num = (first_byte & 0x60) >> 5
        assert conn_num == 0, f"ConnectionNumber should be 0, got {conn_num}"

        # Fragmented flag should be 0 in bit 7
        frag = (first_byte & 0x80) >> 7
        assert frag == 0, f"Fragmented flag should be 0, got {frag}"

    def test_header_byte_with_connection_number(self):
        """Test header with connection number / 测试带连接编号的头部"""
        packet = NetPacket(PacketProperty.CHANNELED, 0)
        packet.connection_number = 2

        first_byte = packet.raw_data[0]

        # ConnectionNumber in bits 5-6
        conn_num = (first_byte & 0x60) >> 5
        assert conn_num == 2, f"ConnectionNumber should be 2, got {conn_num}"

        # Property should still be intact
        prop = first_byte & 0x1F
        assert prop == PacketProperty.CHANNELED

    def test_header_byte_fragmented_flag(self):
        """Test fragmented flag in header / 测试头部中的分片标志"""
        packet = NetPacket(PacketProperty.CHANNELED, 0)
        packet.mark_fragmented()

        first_byte = packet.raw_data[0]

        # Bit 7 should be set
        frag = (first_byte & 0x80) >> 7
        assert frag == 1, f"Fragmented flag should be 1, got {frag}"

    def test_channeled_packet_header_structure(self):
        """Test channeled packet header / 测试通道数据包头部"""
        packet = NetPacket(PacketProperty.CHANNELED, 10)
        packet.sequence = 0x1234
        packet.channel_id = 2

        data = packet.raw_data

        # Byte 0: Property + flags
        assert data[0] == PacketProperty.CHANNELED

        # Bytes 1-2: Sequence (little-endian)
        # C#: BitConverter.ToUInt16(RawData, 1)
        assert data[1] == 0x34  # Low byte
        assert data[2] == 0x12  # High byte

        # Byte 3: ChannelId
        # C#: RawData[3]
        assert data[3] == 2

    def test_fragmented_packet_structure(self):
        """Test fragmented packet structure / 测试分片数据包结构"""
        packet = NetPacket(PacketProperty.CHANNELED, 0)
        packet.mark_fragmented()
        packet.sequence = 100
        packet.fragment_id = 0xABCD
        packet.fragment_part = 3
        packet.fragments_total = 10

        data = packet.raw_data

        # Fragment ID at bytes 4-5 (little-endian)
        # C#: BitConverter.ToUInt16(RawData, 4)
        assert data[4] == 0xCD
        assert data[5] == 0xAB

        # Fragment Part at bytes 6-7 (little-endian)
        # C#: BitConverter.ToUInt16(RawData, 6)
        assert data[6] == 0x03
        assert data[7] == 0x00

        # Fragments Total at bytes 8-9 (little-endian)
        # C#: BitConverter.ToUInt16(RawData, 8)
        assert data[8] == 0x0A
        assert data[9] == 0x00


class TestPacketPropertiesCompatibility:
    """Test all packet properties match C# values / 测试所有数据包属性与 C# 值匹配"""

    def test_all_packet_property_values_in_header(self):
        """Test all packet properties encode correctly in header / 测试所有属性正确编码到头部"""
        for prop in PacketProperty:
            packet = NetPacket(prop, 0)
            first_byte = packet.raw_data[0]
            encoded_prop = first_byte & 0x1F

            assert encoded_prop == prop.value, \
                f"PacketProperty {prop.name} (value={prop.value}) encodes as {encoded_prop} in header"

    def test_packet_property_roundtrip(self):
        """Test packet property roundtrip through header / 测试属性通过头部往返"""
        for prop in PacketProperty:
            packet = NetPacket(prop, 0)
            # Get property back from header
            # C#: (PacketProperty)(RawData[0] & 0x1F)
            read_prop = PacketProperty(packet.raw_data[0] & 0x1F)

            assert read_prop == prop, \
                f"Property roundtrip failed: {prop} -> {read_prop}"


class TestSequenceNumberEncoding:
    """Test sequence number encoding matches C# / 测试序列号编码与 C# 匹配"""

    def test_sequence_little_endian(self):
        """Test sequence is little-endian / 测试序列号为小端"""
        packet = NetPacket(PacketProperty.CHANNELED, 0)
        test_value = 0x1234

        # Write using Python implementation
        packet.sequence = test_value

        # Verify little-endian byte order
        # C#: FastBitConverter.GetBytes(RawData, 1, value)
        assert packet.raw_data[1] == 0x34, \
            f"Low byte should be 0x34, got 0x{packet.raw_data[1]:02X}"
        assert packet.raw_data[2] == 0x12, \
            f"High byte should be 0x12, got 0x{packet.raw_data[2]:02X}"

    def test_sequence_read_write(self):
        """Test sequence read and write / 测试序列号读写"""
        for test_value in [0, 1, 255, 256, 32767, 32768, 65535]:
            packet = NetPacket(PacketProperty.CHANNELED, 0)
            packet.sequence = test_value

            # Read back
            # C#: BitConverter.ToUInt16(RawData, 1)
            read_value = (packet.raw_data[1] & 0xFF) | ((packet.raw_data[2] & 0xFF) << 8)

            assert read_value == test_value, \
                f"Sequence {test_value} roundtrip failed, got {read_value}"

    def test_sequence_wraparound(self):
        """Test sequence wraparound at ushort max / 测试序列号在 ushort 最大值循环"""
        packet = NetPacket(PacketProperty.CHANNELED, 0)

        # Set to max
        packet.sequence = 65535
        assert packet.sequence == 65535

        # Set to 0
        packet.sequence = 0
        assert packet.sequence == 0


class TestHeaderSizes:
    """Test header sizes match C# exactly / 测试头部大小与 C# 完全匹配"""

    def test_header_size_for_all_properties(self):
        """Test header size for all packet properties / 测试所有属性的数据包头部大小"""
        expected_sizes = {
            PacketProperty.UNRELIABLE: 1,
            PacketProperty.CHANNELED: 4,
            PacketProperty.ACK: 4,
            PacketProperty.PING: 3,
            PacketProperty.PONG: 11,
            PacketProperty.CONNECT_REQUEST: 18,
            PacketProperty.CONNECT_ACCEPT: 15,
            PacketProperty.DISCONNECT: 9,
            PacketProperty.UNCONNECTED_MESSAGE: 1,
            PacketProperty.MTU_CHECK: 3,
            PacketProperty.MTU_OK: 1,
            PacketProperty.BROADCAST: 1,
            PacketProperty.MERGED: 1,
            PacketProperty.SHUTDOWN_OK: 1,
            PacketProperty.PEER_NOT_FOUND: 1,
            PacketProperty.INVALID_PROTOCOL: 1,
            PacketProperty.NAT_MESSAGE: 1,
            PacketProperty.EMPTY: 1,
        }

        for prop, expected_size in expected_sizes.items():
            actual_size = get_header_size(prop)
            assert actual_size == expected_size, \
                f"Header size for {prop.name} should be {expected_size} (C# v0.9.5.2), got {actual_size}"


class TestSerializationCompatibility:
    """Test serialization is compatible with C# / 测试序列化与 C# 兼容"""

    def test_int_little_endian(self):
        """Test int is little-endian (C# default) / 测试整型为小端（C# 默认）"""
        writer = NetDataWriter()
        test_value = 0x12345678
        writer.put_int(test_value)

        # Verify byte order
        # C# default: little-endian
        data = writer.data
        assert data[0] == 0x78, f"Byte 0 should be 0x78, got 0x{data[0]:02X}"
        assert data[1] == 0x56, f"Byte 1 should be 0x56, got 0x{data[1]:02X}"
        assert data[2] == 0x34, f"Byte 2 should be 0x34, got 0x{data[2]:02X}"
        assert data[3] == 0x12, f"Byte 3 should be 0x12, got 0x{data[3]:02X}"

    def test_float_encoding(self):
        """Test float encoding matches C# / 测试浮点数编码与 C# 匹配"""
        writer = NetDataWriter()
        test_value = 3.14159
        writer.put_float(test_value)

        # Verify using struct
        data = writer.to_bytes()
        decoded = struct.unpack('<f', data[0:4])[0]

        assert abs(decoded - test_value) < 0.00001, \
            f"Float encoding mismatch: {test_value} vs {decoded}"

    def test_double_encoding(self):
        """Test double encoding matches C# / 测试双精度编码与 C# 匹配"""
        writer = NetDataWriter()
        test_value = 2.718281828459045
        writer.put_double(test_value)

        data = writer.to_bytes()
        decoded = struct.unpack('<d', data[0:8])[0]

        assert abs(decoded - test_value) < 1e-15, \
            f"Double encoding mismatch: {test_value} vs {decoded}"

    def test_string_utf8_encoding(self):
        """Test string UTF-8 encoding matches C# / 测试字符串 UTF-8 编码与 C# 匹配"""
        writer = NetDataWriter()
        test_string = "Hello World"
        writer.put_string(test_string)

        data = writer.to_bytes()

        # Read length prefix (ushort, little-endian)
        length = struct.unpack('<H', data[0:2])[0]

        # C# encodes string as UTF-8 with length prefix
        # For non-empty strings: length = bytes + 1
        assert length == len(test_string.encode('utf-8')) + 1, \
            f"String length prefix should be {len(test_string.encode('utf-8')) + 1}, got {length}"

        # Verify string data
        string_data = data[2:2 + length - 1]
        decoded = string_data.decode('utf-8')

        assert decoded == test_string, \
            f"String encoding failed: expected {test_string}, got {decoded}"

    def test_string_utf8_chinese(self):
        """Test Chinese character UTF-8 encoding / 测试中文字符 UTF-8 编码"""
        writer = NetDataWriter()
        test_string = "你好世界"
        writer.put_string(test_string)

        data = writer.to_bytes()
        reader = NetDataReader(data)
        decoded = reader.get_string()

        assert decoded == test_string, \
            f"Chinese string encoding failed: expected {test_string}, got {decoded}"

    def test_empty_string_encoding(self):
        """Test empty string encoding / 测试空字符串编码"""
        writer = NetDataWriter()
        writer.put_string("")

        data = writer.to_bytes()

        # Empty string should have length 0
        length = struct.unpack('<H', data[0:2])[0]
        assert length == 0, f"Empty string length should be 0, got {length}"
        assert len(data) == 2, f"Empty string should be 2 bytes (length only), got {len(data)}"


class TestPacketVerification:
    """Test packet verification logic matches C# / 测试数据包验证逻辑与 C# 匹配"""

    def test_verify_valid_packet(self):
        """Test verify valid packet / 测试验证有效数据包"""
        for prop in PacketProperty:
            packet = NetPacket(prop, 10)
            assert packet.verify(), f"Packet with property {prop.name} should be valid"

    def test_verify_invalid_property(self):
        """Test verify invalid property / 测试验证无效属性"""
        packet = NetPacket(10)

        # Set invalid property (>= 18)
        # C#: if (property > LastProperty) return false
        packet._data[0] = 18 | 0x1F  # Invalid property value

        assert not packet.verify(), "Packet with invalid property should fail verification"

    def test_verify_size_too_small(self):
        """Test verify with size too small / 测试验证大小过小"""
        packet = NetPacket(PacketProperty.CHANNELED, 0)

        # Set size smaller than header
        # C#: if (Size < headerSize) return false
        packet._size = 2  # CHANNELED header is 4 bytes

        assert not packet.verify(), "Packet with size < header should fail verification"

    def test_verify_fragmented_without_fragment_size(self):
        """Test verify fragmented without fragment header / 测试验证分片但无分片头部"""
        packet = NetPacket(PacketProperty.CHANNELED, 0)
        packet.mark_fragmented()

        # Set size to header only (no room for fragment header)
        # C#: if (fragmented || Size >= headerSize + FragmentHeaderSize)
        packet._size = 4  # Just header, no fragment header

        assert not packet.verify(), \
            "Fragmented packet without fragment header size should fail verification"


class TestMTUValues:
    """Test MTU values match C# v0.9.5.2 / 测试 MTU 值与 C# v0.9.5.2 匹配"""

    def test_possible_mtu_values(self):
        """Test all POSSIBLE_MTU values / 测试所有 POSSIBLE_MTU 值"""
        # C# Reference (NetConstants.cs):
        # 576 - MaxUdpHeaderSize,   // minimal (RFC 1191)
        # 1024,                     // most games standard
        # 1232 - MaxUdpHeaderSize,
        # 1460 - MaxUdpHeaderSize,  // google cloud
        # 1472 - MaxUdpHeaderSize,  // VPN
        # 1492 - MaxUdpHeaderSize,  // Ethernet with LLC and SNAP, PPPoE (RFC 1042)
        # 1500 - MaxUdpHeaderSize   // Ethernet II (RFC 1191)

        expected = [
            576 - 68,   # 508
            1024,       # 1024
            1232 - 68,  # 1164
            1460 - 68,  # 1392
            1472 - 68,  # 1404
            1492 - 68,  # 1424
            1500 - 68,  # 1432
        ]

        assert NetConstants.POSSIBLE_MTU == expected, \
            f"POSSIBLE_MTU doesn't match C# v0.9.5.2.\nExpected: {expected}\nGot: {NetConstants.POSSIBLE_MTU}"


class TestDeliveryMethodValues:
    """Test DeliveryMethod enum values match C# / 测试 DeliveryMethod 枚举值与 C# 匹配"""

    def test_delivery_method_values(self):
        """Test all DeliveryMethod values / 测试所有 DeliveryMethod 值"""
        # C# Reference (NetConstants.cs):
        # Unreliable = 4,
        # ReliableUnordered = 0,
        # Sequenced = 1,
        # ReliableOrdered = 2,
        # ReliableSequenced = 3

        assert DeliveryMethod.UNRELIABLE.value == 4
        assert DeliveryMethod.RELIABLE_UNORDERED.value == 0
        assert DeliveryMethod.SEQUENCED.value == 1
        assert DeliveryMethod.RELIABLE_ORDERED.value == 2
        assert DeliveryMethod.RELIABLE_SEQUENCED.value == 3


class TestProtocolConstants:
    """Test protocol constants match C# / 测试协议常量与 C# 匹配"""

    def test_protocol_id(self):
        """Test PROTOCOL_ID = 11 / 测试 PROTOCOL_ID = 11"""
        # C#: internal const int ProtocolId = 11;
        assert NetConstants.PROTOCOL_ID == 11, \
            f"PROTOCOL_ID must be 11 (C# v0.9.5.2), got {NetConstants.PROTOCOL_ID}"

    def test_max_sequence(self):
        """Test MAX_SEQUENCE = 32768 / 测试 MAX_SEQUENCE = 32768"""
        # C#: public const ushort MaxSequence = 32768;
        assert NetConstants.MAX_SEQUENCE == 32768, \
            f"MAX_SEQUENCE must be 32768 (C#), got {NetConstants.MAX_SEQUENCE}"

    def test_default_window_size(self):
        """Test DEFAULT_WINDOW_SIZE = 64 / 测试 DEFAULT_WINDOW_SIZE = 64"""
        # C#: public const int DefaultWindowSize = 64;
        assert NetConstants.DEFAULT_WINDOW_SIZE == 64, \
            f"DEFAULT_WINDOW_SIZE must be 64 (C#), got {NetConstants.DEFAULT_WINDOW_SIZE}"

    def test_header_sizes(self):
        """Test header size constants / 测试头部大小常量"""
        # C#:
        # public const int HeaderSize = 1;
        # public const int ChanneledHeaderSize = 4;
        # public const int FragmentHeaderSize = 6;

        assert NetConstants.HEADER_SIZE == 1
        assert NetConstants.CHANNELED_HEADER_SIZE == 4
        assert NetConstants.FRAGMENT_HEADER_SIZE == 6


class TestByteLevelPacketCompatibility:
    """Test byte-level packet compatibility / 测试字节级数据包兼容性"""

    def test_packet_bytes_match_expected_format(self):
        """Test packet bytes match expected format / 测试数据包字节匹配预期格式"""
        # Create a packet with specific values
        packet = NetPacket(PacketProperty.CHANNELED, 0)
        packet.connection_number = 2
        packet.sequence = 0x1234
        packet.channel_id = 1

        bytes_data = packet.get_bytes()

        # Verify each byte
        # Byte 0: Property (0-4) + ConnNum (5-6) = CHANNELED (1) | (2 << 5) = 1 | 64 = 65
        assert bytes_data[0] == 65, \
            f"Byte 0 should be 65 (CHANNELED | conn_num=2), got {bytes_data[0]}"

        # Bytes 1-2: Sequence (little-endian)
        assert bytes_data[1] == 0x34, f"Byte 1 should be 0x34, got 0x{bytes_data[1]:02X}"
        assert bytes_data[2] == 0x12, f"Byte 2 should be 0x12, got 0x{bytes_data[2]:02X}"

        # Byte 3: Channel ID
        assert bytes_data[3] == 1, f"Byte 3 should be 1, got {bytes_data[3]}"

    def test_serialization_roundtrip_preserves_bytes(self):
        """Test serialization roundtrip preserves bytes / 测试序列化往返保留字节"""
        original_data = b'\x01\x00\x00\x00TestMessage'

        # Create packet from bytes
        packet = NetPacket.from_bytes(original_data)

        # Get bytes back
        result_data = packet.get_bytes()

        # Should match exactly
        assert result_data == original_data, \
            f"Bytes don't match after roundtrip:\nOriginal: {original_data.hex()}\nResult:   {result_data.hex()}"


class TestACKPacketFormat:
    """Test ACK packet format / 测试 ACK 包格式"""

    def test_ack_packet_structure(self):
        """Test ACK packet structure / 测试 ACK 包结构"""
        # ACK packet has ChanneledHeaderSize + bitmap
        # Bitmap size = (window_size - 1) / 8 + 2
        window_size = NetConstants.DEFAULT_WINDOW_SIZE  # 64
        bitmap_size = (window_size - 1) // 8 + 2  # (64-1)/8 + 2 = 10

        ack = NetPacket(PacketProperty.ACK, bitmap_size)
        ack.sequence = 100
        ack.channel_id = 0

        # Verify structure
        assert ack.packet_property == PacketProperty.ACK
        assert ack.size == NetConstants.CHANNELED_HEADER_SIZE + bitmap_size
        assert ack.sequence == 100
        assert ack.channel_id == 0


class TestBoundaryConditions:
    """Test boundary conditions match C# behavior / 测试边界条件与 C# 行为匹配"""

    def test_connection_number_range(self):
        """Test connection number is 0-3 (2 bits) / 测试连接编号为 0-3（2位）"""
        packet = NetPacket(PacketProperty.CHANNELED, 0)

        for i in range(4):
            packet.connection_number = i
            assert packet.connection_number == i, \
                f"Connection number {i} should be preserved"

        # Test values > 3 are masked
        packet.connection_number = 4
        assert packet.connection_number == 0, \
            "Connection number 4 should be masked to 0"

        packet.connection_number = 7
        assert packet.connection_number == 3, \
            "Connection number 7 should be masked to 3"

    def test_channel_id_range(self):
        """Test channel_id is byte (0-255) / 测试 channel_id 为字节（0-255）"""
        packet = NetPacket(PacketProperty.CHANNELED, 0)

        packet.channel_id = 255
        assert packet.channel_id == 255

        packet.channel_id = 0
        assert packet.channel_id == 0


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
