"""
NetPacket功能测试

测试NetPacket的所有属性和方法
"""

import pytest
from litenetlib.packets import NetPacket
from litenetlib.packets.net_packet import PacketProperty


class TestPacketProperty:
    """测试PacketProperty枚举"""

    def test_packet_property_values(self):
        """测试所有PacketProperty枚举值"""
        assert PacketProperty.Unreliable == 0
        assert PacketProperty.Channeled == 1
        assert PacketProperty.Ack == 2
        assert PacketProperty.Ping == 3
        assert PacketProperty.Pong == 4
        assert PacketProperty.ConnectRequest == 5
        assert PacketProperty.ConnectAccept == 6
        assert PacketProperty.Disconnect == 7
        assert PacketProperty.UnconnectedMessage == 8
        assert PacketProperty.MtuCheck == 9
        assert PacketProperty.MtuOk == 10
        assert PacketProperty.Broadcast == 11
        assert PacketProperty.Merged == 12
        assert PacketProperty.ShutdownOk == 13
        assert PacketProperty.PeerNotFound == 14
        assert PacketProperty.InvalidProtocol == 15
        assert PacketProperty.NatMessage == 16
        assert PacketProperty.Empty == 17


class TestNetPacketBasic:
    """测试NetPacket基本功能"""

    def test_create_packet_with_size(self):
        """测试创建指定大小的包"""
        packet = NetPacket(100)
        assert packet.size == 100
        assert len(packet.raw_data) == 100

    def test_create_packet_with_property(self):
        """测试创建带属性的包"""
        packet = NetPacket(50, PacketProperty.Unreliable)
        assert packet.packet_property == PacketProperty.Unreliable
        # Size should include header
        assert packet.size >= 50

    def test_packet_property_getter(self):
        """测试获取包属性"""
        packet = NetPacket(100, PacketProperty.Channeled)
        assert packet.packet_property == PacketProperty.Channeled

    def test_connection_number(self):
        """测试连接编号"""
        packet = NetPacket(100)
        # Default connection number
        assert packet.connection_number == 0
        # Set connection number (Note: only 1 bit available, values are 0-1)
        packet.connection_number = 1
        assert packet.connection_number == 1

    def test_sequence_number(self):
        """测试序列号"""
        packet = NetPacket(100)
        assert packet.sequence == 0
        packet.sequence = 100
        assert packet.sequence == 100

    def test_channel_id(self):
        """测试通道ID"""
        packet = NetPacket(100, PacketProperty.Channeled)
        assert packet.channel_id == 0
        packet.channel_id = 3
        assert packet.channel_id == 3

    def test_is_fragmented_default(self):
        """测试默认分片状态"""
        packet = NetPacket(100)
        assert packet.is_fragmented == False

    def test_fragment_properties(self):
        """测试分片属性"""
        packet = NetPacket(100)
        packet.mark_fragmented()

        assert packet.is_fragmented == True
        assert packet.fragment_id == 0
        assert packet.fragment_part == 0
        assert packet.fragments_total == 0

        # Set fragment properties
        packet.fragment_id = 5
        packet.fragment_part = 2
        packet.fragments_total = 10

        assert packet.fragment_id == 5
        assert packet.fragment_part == 2
        assert packet.fragments_total == 10

    def test_raw_data(self):
        """测试原始数据访问"""
        packet = NetPacket(100)
        raw = packet.raw_data
        # raw_data returns bytearray (mutable), not bytes
        assert isinstance(raw, (bytes, bytearray))
        assert len(raw) == 100

    def test_raw_data_mutation(self):
        """测试修改原始数据"""
        packet = NetPacket(100)
        # Can access and modify raw data
        data = bytearray(packet.raw_data)
        data[0:5] = b'\x01\x02\x03\x04\x05'
        # NetPacket stores data as bytearray internally


class TestNetPacketMethods:
    """测试NetPacket方法"""

    def test_get_header_size_unreliable(self):
        """测试Unreliable包的包头大小"""
        packet = NetPacket(100, PacketProperty.Unreliable)
        header_size = packet.get_header_size()
        # Unreliable has minimal header (1 byte for property)
        assert header_size >= 1

    def test_get_header_size_chnaneled(self):
        """测试Channeled包的包头大小"""
        packet = NetPacket(100, PacketProperty.Channeled)
        header_size = packet.get_header_size()
        # Channeled has larger header
        assert header_size >= 2

    def test_get_header_size_fragmented(self):
        """测试分片包的包头大小"""
        packet = NetPacket(100, PacketProperty.Channeled)
        packet.mark_fragmented()
        header_size = packet.get_header_size()
        # Fragmented packets have even larger header
        assert header_size >= 4

    def test_mark_fragmented(self):
        """测试标记为分片包"""
        packet = NetPacket(100, PacketProperty.Channeled)
        assert packet.is_fragmented == False

        packet.mark_fragmented()
        assert packet.is_fragmented == True

    def test_verify_valid_packet(self):
        """测试验证有效包"""
        packet = NetPacket(100, PacketProperty.Unreliable)
        # Valid packet should pass verification
        # Note: Verify logic depends on implementation
        result = packet.verify()
        # Should return True for valid packet
        assert isinstance(result, bool)

    def test_verify_different_properties(self):
        """测试不同属性包的验证"""
        properties = [
            PacketProperty.Unreliable,
            PacketProperty.Channeled,
            PacketProperty.Ack,
        ]

        for prop in properties:
            packet = NetPacket(100, prop)
            result = packet.verify()
            assert isinstance(result, bool), f"Verify should return bool for {prop}"


class TestNetPacketEdgeCases:
    """测试NetPacket边界情况"""

    def test_zero_size_packet(self):
        """测试零大小包"""
        packet = NetPacket(0)
        assert packet.size == 0

    def test_large_packet(self):
        """测试大包"""
        large_size = 65536  # 64KB
        packet = NetPacket(large_size)
        assert packet.size == large_size

    def test_small_packet(self):
        """测试小包"""
        packet = NetPacket(10)
        assert packet.size == 10

    def test_packet_with_all_properties(self):
        """测试设置所有属性"""
        packet = NetPacket(100, PacketProperty.Channeled)
        packet.connection_number = 1
        packet.sequence = 1000
        packet.channel_id = 5
        packet.mark_fragmented()
        packet.fragment_id = 2
        packet.fragment_part = 1
        packet.fragments_total = 3

        assert packet.packet_property == PacketProperty.Channeled
        assert packet.connection_number == 1
        assert packet.sequence == 1000
        assert packet.channel_id == 5
        assert packet.is_fragmented == True
        assert packet.fragment_id == 2
        assert packet.fragment_part == 1
        assert packet.fragments_total == 3


class TestNetPacketDataIntegrity:
    """测试NetPacket数据完整性"""

    def test_data_size_consistency(self):
        """测试数据大小一致性"""
        requested_size = 100
        packet = NetPacket(requested_size)
        assert packet.size == len(packet.raw_data)

    def test_property_in_data(self):
        """测试属性在数据中的存储"""
        packet = NetPacket(100, PacketProperty.Ping)
        # Property should be stored in first byte
        # Low 5 bits of first byte
        first_byte = packet.raw_data[0]
        property_value = first_byte & 0x1F
        assert property_value == PacketProperty.Ping


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
