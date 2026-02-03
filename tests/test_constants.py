"""
Protocol Constants Tests / 协议常量测试

Tests for verifying all protocol constants match C# LiteNetLib v0.9.5.2
验证所有协议常量与 C# LiteNetLib v0.9.5.2 匹配的测试

Reference C# Code:
- LiteNetLib/NetConstants.cs
- LiteNetLib/NetPacket.cs (PacketProperty enum)
"""

import pytest
from litenetlib.core.constants import (
    PacketProperty,
    DeliveryMethod,
    DisconnectReason,
    UnconnectedMessageType,
    NetConstants,
    get_header_size
)


class TestPacketProperty:
    """Test PacketProperty enum values / 测试 PacketProperty 枚举值"""

    def test_packet_property_unreliable_value(self):
        """Test UNRELIABLE = 0 / 测试 UNRELIABLE = 0"""
        assert PacketProperty.UNRELIABLE == 0, \
            f"PacketProperty.UNRELIABLE should be 0 (C# v0.9.5.2), got {PacketProperty.UNRELIABLE}"

    def test_packet_property_channeled_value(self):
        """Test CHANNELED = 1 / 测试 CHANNELED = 1"""
        assert PacketProperty.CHANNELED == 1, \
            f"PacketProperty.CHANNELED should be 1 (C# v0.9.5.2), got {PacketProperty.CHANNELED}"

    def test_packet_property_ack_value(self):
        """Test ACK = 2 / 测试 ACK = 2"""
        assert PacketProperty.ACK == 2, \
            f"PacketProperty.ACK should be 2 (C# v0.9.5.2), got {PacketProperty.ACK}"

    def test_packet_property_ping_value(self):
        """Test PING = 3 / 测试 PING = 3"""
        assert PacketProperty.PING == 3, \
            f"PacketProperty.PING should be 3 (C# v0.9.5.2), got {PacketProperty.PING}"

    def test_packet_property_pong_value(self):
        """Test PONG = 4 / 测试 PONG = 4"""
        assert PacketProperty.PONG == 4, \
            f"PacketProperty.PONG should be 4 (C# v0.9.5.2), got {PacketProperty.PONG}"

    def test_packet_property_connect_request_value(self):
        """Test CONNECT_REQUEST = 5 / 测试 CONNECT_REQUEST = 5"""
        assert PacketProperty.CONNECT_REQUEST == 5, \
            f"PacketProperty.CONNECT_REQUEST should be 5 (C# v0.9.5.2), got {PacketProperty.CONNECT_REQUEST}"

    def test_packet_property_connect_accept_value(self):
        """Test CONNECT_ACCEPT = 6 / 测试 CONNECT_ACCEPT = 6"""
        assert PacketProperty.CONNECT_ACCEPT == 6, \
            f"PacketProperty.CONNECT_ACCEPT should be 6 (C# v0.9.5.2), got {PacketProperty.CONNECT_ACCEPT}"

    def test_packet_property_disconnect_value(self):
        """Test DISCONNECT = 7 / 测试 DISCONNECT = 7"""
        assert PacketProperty.DISCONNECT == 7, \
            f"PacketProperty.DISCONNECT should be 7 (C# v0.9.5.2), got {PacketProperty.DISCONNECT}"

    def test_packet_property_unconnected_message_value(self):
        """Test UNCONNECTED_MESSAGE = 8 / 测试 UNCONNECTED_MESSAGE = 8"""
        assert PacketProperty.UNCONNECTED_MESSAGE == 8, \
            f"PacketProperty.UNCONNECTED_MESSAGE should be 8 (C# v0.9.5.2), got {PacketProperty.UNCONNECTED_MESSAGE}"

    def test_packet_property_mtu_check_value(self):
        """Test MTU_CHECK = 9 / 测试 MTU_CHECK = 9"""
        assert PacketProperty.MTU_CHECK == 9, \
            f"PacketProperty.MTU_CHECK should be 9 (C# v0.9.5.2), got {PacketProperty.MTU_CHECK}"

    def test_packet_property_mtu_ok_value(self):
        """Test MTU_OK = 10 / 测试 MTU_OK = 10"""
        assert PacketProperty.MTU_OK == 10, \
            f"PacketProperty.MTU_OK should be 10 (C# v0.9.5.2), got {PacketProperty.MTU_OK}"

    def test_packet_property_broadcast_value(self):
        """Test BROADCAST = 11 / 测试 BROADCAST = 11"""
        assert PacketProperty.BROADCAST == 11, \
            f"PacketProperty.BROADCAST should be 11 (C# v0.9.5.2), got {PacketProperty.BROADCAST}"

    def test_packet_property_merged_value(self):
        """Test MERGED = 12 / 测试 MERGED = 12"""
        assert PacketProperty.MERGED == 12, \
            f"PacketProperty.MERGED should be 12 (C# v0.9.5.2), got {PacketProperty.MERGED}"

    def test_packet_property_shutdown_ok_value(self):
        """Test SHUTDOWN_OK = 13 / 测试 SHUTDOWN_OK = 13"""
        assert PacketProperty.SHUTDOWN_OK == 13, \
            f"PacketProperty.SHUTDOWN_OK should be 13 (C# v0.9.5.2), got {PacketProperty.SHUTDOWN_OK}"

    def test_packet_property_peer_not_found_value(self):
        """Test PEER_NOT_FOUND = 14 / 测试 PEER_NOT_FOUND = 14"""
        assert PacketProperty.PEER_NOT_FOUND == 14, \
            f"PacketProperty.PEER_NOT_FOUND should be 14 (C# v0.9.5.2), got {PacketProperty.PEER_NOT_FOUND}"

    def test_packet_property_invalid_protocol_value(self):
        """Test INVALID_PROTOCOL = 15 / 测试 INVALID_PROTOCOL = 15"""
        assert PacketProperty.INVALID_PROTOCOL == 15, \
            f"PacketProperty.INVALID_PROTOCOL should be 15 (C# v0.9.5.2), got {PacketProperty.INVALID_PROTOCOL}"

    def test_packet_property_nat_message_value(self):
        """Test NAT_MESSAGE = 16 / 测试 NAT_MESSAGE = 16"""
        assert PacketProperty.NAT_MESSAGE == 16, \
            f"PacketProperty.NAT_MESSAGE should be 16 (C# v0.9.5.2), got {PacketProperty.NAT_MESSAGE}"

    def test_packet_property_empty_value(self):
        """Test EMPTY = 17 / 测试 EMPTY = 17"""
        assert PacketProperty.EMPTY == 17, \
            f"PacketProperty.EMPTY should be 17 (C# v0.9.5.2), got {PacketProperty.EMPTY}"

    def test_packet_property_total_count(self):
        """Test total PacketProperty count = 18 (0-17) / 测试 PacketProperty 总数为 18"""
        # C#: LastProperty = Enum.GetValues(typeof(PacketProperty)).Length
        assert len(PacketProperty) == 18, \
            f"PacketProperty should have 18 values (0-17), got {len(PacketProperty)}"


class TestDeliveryMethod:
    """Test DeliveryMethod enum values / 测试 DeliveryMethod 枚举值"""

    def test_delivery_method_unreliable_value(self):
        """Test UNRELIABLE = 4 / 测试 UNRELIABLE = 4"""
        # C# Reference: Unreliable = 4
        assert DeliveryMethod.UNRELIABLE == 4, \
            f"DeliveryMethod.UNRELIABLE should be 4 (C# v0.9.5.2), got {DeliveryMethod.UNRELIABLE}"

    def test_delivery_method_reliable_unordered_value(self):
        """Test RELIABLE_UNORDERED = 0 / 测试 RELIABLE_UNORDERED = 0"""
        # C# Reference: ReliableUnordered = 0
        assert DeliveryMethod.RELIABLE_UNORDERED == 0, \
            f"DeliveryMethod.RELIABLE_UNORDERED should be 0 (C# v0.9.5.2), got {DeliveryMethod.RELIABLE_UNORDERED}"

    def test_delivery_method_sequenced_value(self):
        """Test SEQUENCED = 1 / 测试 SEQUENCED = 1"""
        # C# Reference: Sequenced = 1
        assert DeliveryMethod.SEQUENCED == 1, \
            f"DeliveryMethod.SEQUENCED should be 1 (C# v0.9.5.2), got {DeliveryMethod.SEQUENCED}"

    def test_delivery_method_reliable_ordered_value(self):
        """Test RELIABLE_ORDERED = 2 / 测试 RELIABLE_ORDERED = 2"""
        # C# Reference: ReliableOrdered = 2
        assert DeliveryMethod.RELIABLE_ORDERED == 2, \
            f"DeliveryMethod.RELIABLE_ORDERED should be 2 (C# v0.9.5.2), got {DeliveryMethod.RELIABLE_ORDERED}"

    def test_delivery_method_reliable_sequenced_value(self):
        """Test RELIABLE_SEQUENCED = 3 / 测试 RELIABLE_SEQUENCED = 3"""
        # C# Reference: ReliableSequenced = 3
        assert DeliveryMethod.RELIABLE_SEQUENCED == 3, \
            f"DeliveryMethod.RELIABLE_SEQUENCED should be 3 (C# v0.9.5.2), got {DeliveryMethod.RELIABLE_SEQUENCED}"

    def test_delivery_method_total_count(self):
        """Test total DeliveryMethod count = 5 / 测试 DeliveryMethod 总数为 5"""
        assert len(DeliveryMethod) == 5, \
            f"DeliveryMethod should have 5 values, got {len(DeliveryMethod)}"


class TestDisconnectReason:
    """Test DisconnectReason enum values / 测试 DisconnectReason 枚举值"""

    def test_disconnect_reason_values(self):
        """Test all DisconnectReason values / 测试所有 DisconnectReason 值"""
        assert DisconnectReason.CONNECTION_FAILED == 0
        assert DisconnectReason.TIMEOUT == 1
        assert DisconnectReason.HOST_UNREACHABLE == 2
        assert DisconnectReason.NETWORK_UNREACHABLE == 3
        assert DisconnectReason.REMOTE_CONNECTION_CLOSE == 4
        assert DisconnectReason.DISCONNECT_PEER_CALLED == 5
        assert DisconnectReason.CONNECTION_REJECTED == 6
        assert DisconnectReason.INVALID_PROTOCOL == 7
        assert DisconnectReason.UNKNOWN_HOST == 8
        assert DisconnectReason.RECONNECT == 9
        assert DisconnectReason.PEER_TO_PEER_CONNECTION == 10
        assert DisconnectReason.PEER_NOT_FOUND == 11


class TestNetConstants:
    """Test NetConstants values / 测试 NetConstants 值"""

    def test_protocol_id(self):
        """Test PROTOCOL_ID = 11 / 测试 PROTOCOL_ID = 11"""
        # C# Reference: internal const int ProtocolId = 11;
        assert NetConstants.PROTOCOL_ID == 11, \
            f"PROTOCOL_ID should be 11 (C# v0.9.5.2), got {NetConstants.PROTOCOL_ID}"

    def test_default_window_size(self):
        """Test DEFAULT_WINDOW_SIZE = 64 / 测试 DEFAULT_WINDOW_SIZE = 64"""
        # C# Reference: public const int DefaultWindowSize = 64;
        assert NetConstants.DEFAULT_WINDOW_SIZE == 64, \
            f"DEFAULT_WINDOW_SIZE should be 64, got {NetConstants.DEFAULT_WINDOW_SIZE}"

    def test_socket_buffer_size(self):
        """Test SOCKET_BUFFER_SIZE = 1MB / 测试 SOCKET_BUFFER_SIZE = 1MB"""
        # C# Reference: public const int SocketBufferSize = 1024 * 1024;
        assert NetConstants.SOCKET_BUFFER_SIZE == 1024 * 1024, \
            f"SOCKET_BUFFER_SIZE should be {1024 * 1024}, got {NetConstants.SOCKET_BUFFER_SIZE}"

    def test_socket_ttl(self):
        """Test SOCKET_TTL = 255 / 测试 SOCKET_TTL = 255"""
        # C# Reference: public const int SocketTTL = 255;
        assert NetConstants.SOCKET_TTL == 255, \
            f"SOCKET_TTL should be 255, got {NetConstants.SOCKET_TTL}"

    def test_header_size(self):
        """Test HEADER_SIZE = 1 / 测试 HEADER_SIZE = 1"""
        # C# Reference: public const int HeaderSize = 1;
        assert NetConstants.HEADER_SIZE == 1, \
            f"HEADER_SIZE should be 1, got {NetConstants.HEADER_SIZE}"

    def test_channeled_header_size(self):
        """Test CHANNELED_HEADER_SIZE = 4 / 测试 CHANNELED_HEADER_SIZE = 4"""
        # C# Reference: public const int ChanneledHeaderSize = 4;
        assert NetConstants.CHANNELED_HEADER_SIZE == 4, \
            f"CHANNELED_HEADER_SIZE should be 4, got {NetConstants.CHANNELED_HEADER_SIZE}"

    def test_fragment_header_size(self):
        """Test FRAGMENT_HEADER_SIZE = 6 / 测试 FRAGMENT_HEADER_SIZE = 6"""
        # C# Reference: public const int FragmentHeaderSize = 6;
        assert NetConstants.FRAGMENT_HEADER_SIZE == 6, \
            f"FRAGMENT_HEADER_SIZE should be 6, got {NetConstants.FRAGMENT_HEADER_SIZE}"

    def test_fragmented_header_total_size(self):
        """Test FRAGMENTED_HEADER_TOTAL_SIZE / 测试 FRAGMENTED_HEADER_TOTAL_SIZE"""
        # C# Reference: public const int FragmentedHeaderTotalSize = ChanneledHeaderSize + FragmentHeaderSize;
        expected = NetConstants.CHANNELED_HEADER_SIZE + NetConstants.FRAGMENT_HEADER_SIZE
        assert NetConstants.FRAGMENTED_HEADER_TOTAL_SIZE == expected, \
            f"FRAGMENTED_HEADER_TOTAL_SIZE should be {expected}, got {NetConstants.FRAGMENTED_HEADER_TOTAL_SIZE}"

    def test_max_sequence(self):
        """Test MAX_SEQUENCE = 32768 / 测试 MAX_SEQUENCE = 32768"""
        # C# Reference: public const ushort MaxSequence = 32768;
        assert NetConstants.MAX_SEQUENCE == 32768, \
            f"MAX_SEQUENCE should be 32768, got {NetConstants.MAX_SEQUENCE}"

    def test_half_max_sequence(self):
        """Test HALF_MAX_SEQUENCE = 16384 / 测试 HALF_MAX_SEQUENCE = 16384"""
        # C# Reference: public const ushort HalfMaxSequence = MaxSequence / 2;
        assert NetConstants.HALF_MAX_SEQUENCE == 16384, \
            f"HALF_MAX_SEQUENCE should be 16384, got {NetConstants.HALF_MAX_SEQUENCE}"

    def test_max_udp_header_size(self):
        """Test MAX_UDP_HEADER_SIZE = 68 / 测试 MAX_UDP_HEADER_SIZE = 68"""
        # C# Reference: internal const int MaxUdpHeaderSize = 68;
        assert NetConstants.MAX_UDP_HEADER_SIZE == 68, \
            f"MAX_UDP_HEADER_SIZE should be 68, got {NetConstants.MAX_UDP_HEADER_SIZE}"

    def test_max_connection_number(self):
        """Test MAX_CONNECTION_NUMBER = 4 / 测试 MAX_CONNECTION_NUMBER = 4"""
        # C# Reference: public const byte MaxConnectionNumber = 4;
        assert NetConstants.MAX_CONNECTION_NUMBER == 4, \
            f"MAX_CONNECTION_NUMBER should be 4, got {NetConstants.MAX_CONNECTION_NUMBER}"

    def test_packet_pool_size(self):
        """Test PACKET_POOL_SIZE = 1000 / 测试 PACKET_POOL_SIZE = 1000"""
        # C# Reference: public const int PacketPoolSize = 1000;
        assert NetConstants.PACKET_POOL_SIZE == 1000, \
            f"PACKET_POOL_SIZE should be 1000, got {NetConstants.PACKET_POOL_SIZE}"


class TestMtuOptions:
    """Test MTU options / 测试 MTU 选项"""

    def test_possible_mtu_count(self):
        """Test POSSIBLE_MTU has 7 options / 测试 POSSIBLE_MTU 有 7 个选项"""
        # C# Reference: PossibleMtu array has 7 values in v0.9.5.2
        assert len(NetConstants.POSSIBLE_MTU) == 7, \
            f"POSSIBLE_MTU should have 7 options (C# v0.9.5.2), got {len(NetConstants.POSSIBLE_MTU)}"

    def test_possible_mtu_values(self):
        """Test all POSSIBLE_MTU values match C# / 测试所有 POSSIBLE_MTU 值与 C# 匹配"""
        # C# Reference:
        # 576 - MaxUdpHeaderSize,   // minimal (RFC 1191)
        # 1024,                     // most games standard
        # 1232 - MaxUdpHeaderSize,
        # 1460 - MaxUdpHeaderSize,  // google cloud
        # 1472 - MaxUdpHeaderSize,  // VPN
        # 1492 - MaxUdpHeaderSize,  // Ethernet with LLC and SNAP, PPPoE (RFC 1042)
        # 1500 - MaxUdpHeaderSize   // Ethernet II (RFC 1191)

        expected_values = [
            576 - 68,   # 508
            1024,       # 1024
            1232 - 68,  # 1164
            1460 - 68,  # 1392
            1472 - 68,  # 1404
            1492 - 68,  # 1424
            1500 - 68,  # 1432
        ]

        assert NetConstants.POSSIBLE_MTU == expected_values, \
            f"POSSIBLE_MTU values don't match C# v0.9.5.2. Expected {expected_values}, got {NetConstants.POSSIBLE_MTU}"

    def test_initial_mtu(self):
        """Test INITIAL_MTU is first option / 测试 INITIAL_MTU 是第一个选项"""
        assert NetConstants.INITIAL_MTU == NetConstants.POSSIBLE_MTU[0], \
            f"INITIAL_MTU should be {NetConstants.POSSIBLE_MTU[0]}, got {NetConstants.INITIAL_MTU}"

    def test_max_packet_size(self):
        """Test MAX_PACKET_SIZE is last option / 测试 MAX_PACKET_SIZE 是最后一个选项"""
        assert NetConstants.MAX_PACKET_SIZE == NetConstants.POSSIBLE_MTU[-1], \
            f"MAX_PACKET_SIZE should be {NetConstants.POSSIBLE_MTU[-1]}, got {NetConstants.MAX_PACKET_SIZE}"

    def test_mtu_increasing_order(self):
        """Test MTU values are in increasing order / 测试 MTU 值递增"""
        for i in range(len(NetConstants.POSSIBLE_MTU) - 1):
            assert NetConstants.POSSIBLE_MTU[i] < NetConstants.POSSIBLE_MTU[i + 1], \
                f"POSSIBLE_MTU[{i}] ({NetConstants.POSSIBLE_MTU[i]}) should be less than POSSIBLE_MTU[{i+1}] ({NetConstants.POSSIBLE_MTU[i+1]})"


class TestHeaderSizes:
    """Test header size mappings / 测试头部大小映射"""

    def test_header_size_unreliable(self):
        """Test UNRELIABLE header size / 测试 UNRELIABLE 头部大小"""
        # C# Reference: default HeaderSize = 1
        assert get_header_size(PacketProperty.UNRELIABLE) == 1, \
            f"UNRELIABLE header size should be 1, got {get_header_size(PacketProperty.UNRELIABLE)}"

    def test_header_size_channeled(self):
        """Test CHANNELED header size / 测试 CHANNELED 头部大小"""
        # C# Reference: ChanneledHeaderSize = 4
        assert get_header_size(PacketProperty.CHANNELED) == 4, \
            f"CHANNELED header size should be 4, got {get_header_size(PacketProperty.CHANNELED)}"

    def test_header_size_ack(self):
        """Test ACK header size / 测试 ACK 头部大小"""
        # C# Reference: ChanneledHeaderSize = 4
        assert get_header_size(PacketProperty.ACK) == 4, \
            f"ACK header size should be 4, got {get_header_size(PacketProperty.ACK)}"

    def test_header_size_ping(self):
        """Test PING header size / 测试 PING 头部大小"""
        # C# Reference: HeaderSize + 2 = 3
        assert get_header_size(PacketProperty.PING) == 3, \
            f"PING header size should be 3, got {get_header_size(PacketProperty.PING)}"

    def test_header_size_pong(self):
        """Test PONG header size / 测试 PONG 头部大小"""
        # C# Reference: HeaderSize + 10 = 11
        assert get_header_size(PacketProperty.PONG) == 11, \
            f"PONG header size should be 11, got {get_header_size(PacketProperty.PONG)}"

    def test_header_size_connect_request(self):
        """Test CONNECT_REQUEST header size / 测试 CONNECT_REQUEST 头部大小"""
        # C# Reference: NetConnectRequestPacket.HeaderSize = 18 (includes base header)
        assert get_header_size(PacketProperty.CONNECT_REQUEST) == 18, \
            f"CONNECT_REQUEST header size should be 18, got {get_header_size(PacketProperty.CONNECT_REQUEST)}"

    def test_header_size_connect_accept(self):
        """Test CONNECT_ACCEPT header size / 测试 CONNECT_ACCEPT 头部大小"""
        # C# Reference: NetConnectAcceptPacket.Size = 15
        assert get_header_size(PacketProperty.CONNECT_ACCEPT) == 15, \
            f"CONNECT_ACCEPT header size should be 15, got {get_header_size(PacketProperty.CONNECT_ACCEPT)}"

    def test_header_size_disconnect(self):
        """Test DISCONNECT header size / 测试 DISCONNECT 头部大小"""
        # C# Reference: HeaderSize + 8 = 9
        assert get_header_size(PacketProperty.DISCONNECT) == 9, \
            f"DISCONNECT header size should be 9, got {get_header_size(PacketProperty.DISCONNECT)}"

    def test_header_size_unconnected_message(self):
        """Test UNCONNECTED_MESSAGE header size / 测试 UNCONNECTED_MESSAGE 头部大小"""
        # C# Reference: default HeaderSize = 1
        assert get_header_size(PacketProperty.UNCONNECTED_MESSAGE) == 1, \
            f"UNCONNECTED_MESSAGE header size should be 1, got {get_header_size(PacketProperty.UNCONNECTED_MESSAGE)}"

    def test_header_size_mtu_check(self):
        """Test MTU_CHECK header size / 测试 MTU_CHECK 头部大小"""
        # C# Reference: HeaderSize + 2 = 3
        assert get_header_size(PacketProperty.MTU_CHECK) == 3, \
            f"MTU_CHECK header size should be 3, got {get_header_size(PacketProperty.MTU_CHECK)}"

    def test_header_size_mtu_ok(self):
        """Test MTU_OK header size / 测试 MTU_OK 头部大小"""
        # C# Reference: default HeaderSize = 1
        assert get_header_size(PacketProperty.MTU_OK) == 1, \
            f"MTU_OK header size should be 1, got {get_header_size(PacketProperty.MTU_OK)}"

    def test_header_size_broadcast(self):
        """Test BROADCAST header size / 测试 BROADCAST 头部大小"""
        # C# Reference: default HeaderSize = 1
        assert get_header_size(PacketProperty.BROADCAST) == 1, \
            f"BROADCAST header size should be 1, got {get_header_size(PacketProperty.BROADCAST)}"

    def test_header_size_merged(self):
        """Test MERGED header size / 测试 MERGED 头部大小"""
        # C# Reference: default HeaderSize = 1
        assert get_header_size(PacketProperty.MERGED) == 1, \
            f"MERGED header size should be 1, got {get_header_size(PacketProperty.MERGED)}"

    def test_header_size_shutdown_ok(self):
        """Test SHUTDOWN_OK header size / 测试 SHUTDOWN_OK 头部大小"""
        # C# Reference: default HeaderSize = 1
        assert get_header_size(PacketProperty.SHUTDOWN_OK) == 1, \
            f"SHUTDOWN_OK header size should be 1, got {get_header_size(PacketProperty.SHUTDOWN_OK)}"

    def test_header_size_peer_not_found(self):
        """Test PEER_NOT_FOUND header size / 测试 PEER_NOT_FOUND 头部大小"""
        # C# Reference: default HeaderSize = 1
        assert get_header_size(PacketProperty.PEER_NOT_FOUND) == 1, \
            f"PEER_NOT_FOUND header size should be 1, got {get_header_size(PacketProperty.PEER_NOT_FOUND)}"

    def test_header_size_invalid_protocol(self):
        """Test INVALID_PROTOCOL header size / 测试 INVALID_PROTOCOL 头部大小"""
        # C# Reference: default HeaderSize = 1
        assert get_header_size(PacketProperty.INVALID_PROTOCOL) == 1, \
            f"INVALID_PROTOCOL header size should be 1, got {get_header_size(PacketProperty.INVALID_PROTOCOL)}"

    def test_header_size_nat_message(self):
        """Test NAT_MESSAGE header size / 测试 NAT_MESSAGE 头部大小"""
        # C# Reference: default HeaderSize = 1
        assert get_header_size(PacketProperty.NAT_MESSAGE) == 1, \
            f"NAT_MESSAGE header size should be 1, got {get_header_size(PacketProperty.NAT_MESSAGE)}"

    def test_header_size_empty(self):
        """Test EMPTY header size / 测试 EMPTY 头部大小"""
        # C# Reference: default HeaderSize = 1
        assert get_header_size(PacketProperty.EMPTY) == 1, \
            f"EMPTY header size should be 1, got {get_header_size(PacketProperty.EMPTY)}"


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
