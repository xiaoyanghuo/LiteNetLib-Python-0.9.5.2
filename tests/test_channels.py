"""
Channel Tests / 通道测试

Tests for channel classes including BaseChannel, ReliableChannel,
and SequencedChannel.

Reference C# Code: LiteNetLib/Internal/ReliableChannel.cs, SequencedChannel.cs
"""

import pytest
import asyncio
from unittest.mock import Mock, MagicMock
from litenetlib.channels.base_channel import BaseChannel
from litenetlib.channels.reliable_channel import ReliableChannel, PendingPacket
from litenetlib.core.packet import NetPacket
from litenetlib.core.constants import PacketProperty, DeliveryMethod, NetConstants, get_header_size


class MockPeer:
    """Mock peer for testing / 模拟 peer 用于测试"""

    def __init__(self):
        self.sent_packets = []
        self.reliable_packets = []
        self.recycled_packets = []
        self.resend_delay = 300  # milliseconds

    def send_user_data(self, packet):
        """Mock send user data"""
        self.sent_packets.append(packet)

    def add_reliable_packet(self, method, packet):
        """Mock add reliable packet"""
        self.reliable_packets.append((method, packet))

    def recycle_and_deliver(self, packet):
        """Mock recycle and deliver"""
        self.recycled_packets.append(packet)

    def add_channel_to_send_queue(self, channel):
        """Mock add channel to send queue"""
        pass


class ConcreteBaseChannel(BaseChannel):
    """Concrete implementation of BaseChannel for testing / 用于测试的 BaseChannel 具体实现"""

    def send_next_packets(self) -> bool:
        """Send next packets from queue"""
        return False

    def process_packet(self, packet: NetPacket) -> bool:
        """Process incoming packet"""
        return False


class TestBaseChannel:
    """Test BaseChannel functionality / 测试 BaseChannel 功能"""

    def test_base_channel_creation(self):
        """Test creating BaseChannel / 测试创建 BaseChannel"""
        peer = MockPeer()
        channel = ConcreteBaseChannel(peer)
        assert channel._peer == peer
        assert channel.packets_in_queue == 0

    def test_packets_in_queue_property(self):
        """Test packets_in_queue property / 测试 packets_in_queue 属性"""
        peer = MockPeer()
        channel = ConcreteBaseChannel(peer)
        assert channel.packets_in_queue == 0

    def test_add_to_queue(self):
        """Test add_to_queue / 测试添加到队列"""
        peer = MockPeer()
        channel = ConcreteBaseChannel(peer)
        packet = NetPacket(PacketProperty.CHANNELED, 10)

        channel.add_to_queue(packet)
        assert channel.packets_in_queue == 1

    def test_mark_sent(self):
        """Test mark_sent / 测试标记已发送"""
        peer = MockPeer()
        channel = ConcreteBaseChannel(peer)
        channel._is_added_to_peer_channel_send_queue = 1
        channel.mark_sent()
        assert channel._is_added_to_peer_channel_send_queue == 0

    def test_repr(self):
        """Test __repr__ / 测试字符串表示"""
        peer = MockPeer()
        channel = ConcreteBaseChannel(peer)
        repr_str = repr(channel)
        assert 'BaseChannel' in repr_str


class TestPendingPacket:
    """Test PendingPacket functionality / 测试 PendingPacket 功能"""

    def test_pending_packet_creation(self):
        """Test creating PendingPacket / 测试创建 PendingPacket"""
        pp = PendingPacket()
        assert pp._packet is None
        assert pp._is_sent is False
        assert pp._timestamp == 0.0

    def test_pending_packet_init(self):
        """Test PendingPacket.init / 测试 PendingPacket.init"""
        pp = PendingPacket()
        packet = NetPacket(PacketProperty.CHANNELED, 10)
        pp.init(packet)

        assert pp._packet == packet
        assert pp._is_sent is False

    def test_pending_packet_try_send_first_time(self):
        """Test try_send first time / 测试首次 try_send"""
        pp = PendingPacket()
        packet = NetPacket(PacketProperty.CHANNELED, 10)
        pp.init(packet)

        peer = MockPeer()
        result = pp.try_send(0.0, peer)

        assert result is True
        assert pp._is_sent is True
        assert len(peer.sent_packets) == 1

    def test_pending_packet_try_send_waiting(self):
        """Test try_send waiting for resend delay / 测试等待重发延迟"""
        pp = PendingPacket()
        packet = NetPacket(PacketProperty.CHANNELED, 10)
        pp.init(packet)

        peer = MockPeer()
        peer.resend_delay = 500  # 500ms

        # First send
        pp.try_send(0.0, peer)

        # Try again immediately - should not send
        result = pp.try_send(0.1, peer)  # Only 100ms passed
        assert result is True  # Still has packet
        assert len(peer.sent_packets) == 1  # No new send

    def test_pending_packet_try_send_resend(self):
        """Test try_send resend after delay / 测试延迟后重发"""
        pp = PendingPacket()
        packet = NetPacket(PacketProperty.CHANNELED, 10)
        pp.init(packet)

        peer = MockPeer()
        peer.resend_delay = 100  # 100ms

        # First send
        pp.try_send(0.0, peer)

        # Try again after delay - should resend
        result = pp.try_send(0.2, peer)  # 200ms passed
        assert result is True
        assert len(peer.sent_packets) == 2  # Resent

    def test_pending_packet_clear(self):
        """Test clear / 测试清除"""
        pp = PendingPacket()
        packet = NetPacket(PacketProperty.CHANNELED, 10)
        pp.init(packet)

        peer = MockPeer()
        result = pp.clear(peer)

        assert result is True
        assert pp._packet is None
        assert len(peer.recycled_packets) == 1

    def test_pending_packet_clear_empty(self):
        """Test clear when already empty / 测试清除空包"""
        pp = PendingPacket()
        peer = MockPeer()
        result = pp.clear(peer)

        assert result is False

    def test_pending_packet_repr(self):
        """Test __repr__ / 测试字符串表示"""
        pp = PendingPacket()
        assert repr(pp) == "Empty"

        packet = NetPacket(PacketProperty.CHANNELED, 10)
        packet.sequence = 42
        pp.init(packet)
        assert "42" in repr(pp)


class TestReliableChannel:
    """Test ReliableChannel functionality / 测试 ReliableChannel 功能"""

    def test_reliable_channel_creation_ordered(self):
        """Test creating ordered ReliableChannel / 测试创建有序 ReliableChannel"""
        peer = MockPeer()
        channel = ReliableChannel(peer, ordered=True, channel_id=0)

        assert channel._ordered is True
        assert channel._id == 0
        assert channel._delivery_method == DeliveryMethod.RELIABLE_ORDERED
        assert channel._window_size == NetConstants.DEFAULT_WINDOW_SIZE

    def test_reliable_channel_creation_unordered(self):
        """Test creating unordered ReliableChannel / 测试创建无序 ReliableChannel"""
        peer = MockPeer()
        channel = ReliableChannel(peer, ordered=False, channel_id=1)

        assert channel._ordered is False
        assert channel._id == 1
        assert channel._delivery_method == DeliveryMethod.RELIABLE_UNORDERED

    def test_reliable_channel_initial_state(self):
        """Test initial state / 测试初始状态"""
        peer = MockPeer()
        channel = ReliableChannel(peer, ordered=True, channel_id=0)

        assert channel._local_sequence == 0
        assert channel._remote_sequence == 0
        assert channel._local_window_start == 0
        assert channel._remote_window_start == 0
        assert channel._must_send_acks is False

    def test_reliable_channel_pending_packets_array(self):
        """Test pending packets array initialization / 测试待发送包数组初始化"""
        peer = MockPeer()
        channel = ReliableChannel(peer, ordered=True, channel_id=0)

        assert len(channel._pending_packets) == NetConstants.DEFAULT_WINDOW_SIZE
        assert all(isinstance(pp, PendingPacket) for pp in channel._pending_packets)

    def test_reliable_channel_ack_packet(self):
        """Test ACK packet creation / 测试 ACK 包创建"""
        peer = MockPeer()
        channel = ReliableChannel(peer, ordered=True, channel_id=0)

        assert channel._outgoing_acks is not None
        assert channel._outgoing_acks.packet_property == PacketProperty.ACK
        assert channel._outgoing_acks.channel_id == 0

    def test_add_to_queue(self):
        """Test add_to_queue / 测试添加到队列"""
        peer = MockPeer()
        channel = ReliableChannel(peer, ordered=True, channel_id=0)

        packet = NetPacket(PacketProperty.CHANNELED, 10)
        channel.add_to_queue(packet)

        assert channel.packets_in_queue == 1

    def test_send_next_packets_empty(self):
        """Test send_next_packets with empty queue / 测试空队列时发送"""
        peer = MockPeer()
        channel = ReliableChannel(peer, ordered=True, channel_id=0)

        result = channel.send_next_packets()
        assert result is False  # Nothing to send

    def test_send_next_packets_with_data(self):
        """Test send_next_packets with data / 测试有数据时发送"""
        peer = MockPeer()
        channel = ReliableChannel(peer, ordered=True, channel_id=0)

        # Add packet to queue
        packet = NetPacket(PacketProperty.CHANNELED, 10)
        channel.add_to_queue(packet)

        result = channel.send_next_packets()
        # Returns True because packet is pending (waiting for ACK)
        assert result is True  # Pending packet waiting for ACK
        assert len(peer.sent_packets) == 1

        sent_packet = peer.sent_packets[0]
        assert sent_packet.sequence == 0
        assert sent_packet.channel_id == 0

    def test_send_next_packets_sequence_increment(self):
        """Test sequence number increment / 测试序列号递增"""
        peer = MockPeer()
        channel = ReliableChannel(peer, ordered=True, channel_id=0)

        # Send multiple packets
        for i in range(5):
            packet = NetPacket(PacketProperty.CHANNELED, 10)
            channel.add_to_queue(packet)
            channel.send_next_packets()

        assert len(peer.sent_packets) == 5
        assert peer.sent_packets[0].sequence == 0
        assert peer.sent_packets[1].sequence == 1
        assert peer.sent_packets[2].sequence == 2
        assert peer.sent_packets[3].sequence == 3
        assert peer.sent_packets[4].sequence == 4

    def test_process_ack_packet(self):
        """Test processing ACK packet / 测试处理 ACK 包"""
        peer = MockPeer()
        channel = ReliableChannel(peer, ordered=True, channel_id=0)

        # Send a packet
        packet = NetPacket(PacketProperty.CHANNELED, 10)
        channel.add_to_queue(packet)
        channel.send_next_packets()

        # Create ACK packet from peer acknowledging sequence 0
        # The ACK packet size must match _outgoing_acks.size exactly
        # NetPacket adds header size, so we need to subtract it
        ack_data_size = channel._outgoing_acks.size - get_header_size(PacketProperty.ACK)
        ack_packet = NetPacket(PacketProperty.ACK, ack_data_size)
        ack_packet.sequence = 0  # Peer's window start
        ack_packet.channel_id = 0
        # Set bit 0 in the bitmap to acknowledge sequence 0
        # Bitmap starts after CHANNELED_HEADER_SIZE (4 bytes)
        # Bit 0 corresponds to sequence 0
        ack_packet._data[NetConstants.CHANNELED_HEADER_SIZE] = 0x01  # Set bit 0

        # Process ACK
        result = channel.process_packet(ack_packet)
        assert result is False  # ACK packets return False

        # Window should have advanced
        assert channel._local_window_start == 1

    def test_process_data_packet_in_order(self):
        """Test processing in-order packet / 测试处理按序数据包"""
        peer = MockPeer()
        channel = ReliableChannel(peer, ordered=True, channel_id=0)

        # Create packet with sequence 0
        packet = NetPacket(PacketProperty.CHANNELED, 10)
        packet.sequence = 0
        packet.channel_id = 0

        result = channel.process_packet(packet)
        assert result is True
        assert len(peer.reliable_packets) == 1
        assert channel._remote_sequence == 1  # Advanced

    def test_process_data_packet_out_of_order(self):
        """Test processing out-of-order packet / 测试处理乱序数据包"""
        peer = MockPeer()
        channel = ReliableChannel(peer, ordered=True, channel_id=0)

        # Create packet with sequence 1 (before sequence 0)
        packet = NetPacket(PacketProperty.CHANNELED, 10)
        packet.sequence = 1
        packet.channel_id = 0

        result = channel.process_packet(packet)
        assert result is True
        assert len(peer.reliable_packets) == 0  # Not delivered yet, held
        assert channel._remote_sequence == 0  # Not advanced

        # Now send sequence 0
        packet0 = NetPacket(PacketProperty.CHANNELED, 10)
        packet0.sequence = 0
        packet0.channel_id = 0

        channel.process_packet(packet0)
        # Both should be delivered now
        assert len(peer.reliable_packets) == 2
        assert channel._remote_sequence == 2  # Advanced past both

    def test_process_duplicate_packet(self):
        """Test processing duplicate packet / 测试处理重复数据包"""
        peer = MockPeer()
        channel = ReliableChannel(peer, ordered=True, channel_id=0)

        # Send packet
        packet = NetPacket(PacketProperty.CHANNELED, 10)
        packet.sequence = 0
        packet.channel_id = 0

        result1 = channel.process_packet(packet)
        result2 = channel.process_packet(packet)  # Duplicate

        assert result1 is True
        assert result2 is False  # Duplicate rejected
        assert len(peer.reliable_packets) == 1  # Only one delivered

    def test_process_packet_invalid_sequence(self):
        """Test processing packet with invalid sequence / 测试处理无效序列号数据包"""
        peer = MockPeer()
        channel = ReliableChannel(peer, ordered=True, channel_id=0)

        # Create packet with sequence >= MAX_SEQUENCE
        packet = NetPacket(PacketProperty.CHANNELED, 10)
        packet.sequence = NetConstants.MAX_SEQUENCE
        packet.channel_id = 0

        result = channel.process_packet(packet)
        assert result is False

    def test_unordered_channel_immediate_delivery(self):
        """Test unordered channel delivers immediately / 测试无序通道立即发送"""
        peer = MockPeer()
        channel = ReliableChannel(peer, ordered=False, channel_id=0)

        # Send packets out of order
        for seq in [5, 2, 8, 1]:
            packet = NetPacket(PacketProperty.CHANNELED, 10)
            packet.sequence = seq
            packet.channel_id = 0
            channel.process_packet(packet)

        # All should be delivered immediately (unordered)
        assert len(peer.reliable_packets) == 4

    def test_window_size_limit(self):
        """Test window size limit / 测试窗口大小限制"""
        peer = MockPeer()
        channel = ReliableChannel(peer, ordered=True, channel_id=0)

        # Fill window
        for i in range(NetConstants.DEFAULT_WINDOW_SIZE):
            packet = NetPacket(PacketProperty.CHANNELED, 10)
            channel.add_to_queue(packet)

        # Should have sent exactly window_size packets
        channel.send_next_packets()
        packets_sent = len(peer.sent_packets)
        assert packets_sent <= NetConstants.DEFAULT_WINDOW_SIZE

    def test_ack_packet_format(self):
        """Test ACK packet format / 测试 ACK 包格式"""
        peer = MockPeer()
        channel = ReliableChannel(peer, ordered=True, channel_id=0)

        ack_packet = channel._outgoing_acks
        assert ack_packet.packet_property == PacketProperty.ACK
        assert ack_packet.channel_id == 0
        assert ack_packet.size >= NetConstants.CHANNELED_HEADER_SIZE

    def test_must_send_acks_flag(self):
        """Test _must_send_acks flag / 测试 _must_send_acks 标志"""
        peer = MockPeer()
        channel = ReliableChannel(peer, ordered=True, channel_id=0)

        assert channel._must_send_acks is False

        # Process a packet
        packet = NetPacket(PacketProperty.CHANNELED, 10)
        packet.sequence = 0
        packet.channel_id = 0
        channel.process_packet(packet)

        assert channel._must_send_acks is True


class TestChannelSequences:
    """Test sequence number handling / 测试序列号处理"""

    def test_sequence_wraparound(self):
        """Test sequence wraparound / 测试序列号循环"""
        peer = MockPeer()
        channel = ReliableChannel(peer, ordered=True, channel_id=0)

        # Set sequence near max
        channel._local_sequence = NetConstants.MAX_SEQUENCE - 5

        # Send packets
        for i in range(10):
            packet = NetPacket(PacketProperty.CHANNELED, 10)
            channel.add_to_queue(packet)
            channel.send_next_packets()

        # Should wrap around
        assert channel._local_sequence < NetConstants.MAX_SEQUENCE

    def test_relative_sequence_validation(self):
        """Test relative sequence validation / 测试相对序列号验证"""
        peer = MockPeer()
        channel = ReliableChannel(peer, ordered=True, channel_id=0)

        # Set remote window start
        channel._remote_window_start = 100
        channel._remote_sequence = 100

        # Create packet within window
        packet = NetPacket(PacketProperty.CHANNELED, 10)
        packet.sequence = 105
        packet.channel_id = 0

        result = channel.process_packet(packet)
        assert result is True

    def test_old_packet_rejection(self):
        """Test old packet rejection / 测试旧数据包拒绝"""
        peer = MockPeer()
        channel = ReliableChannel(peer, ordered=True, channel_id=0)

        # Set remote window start to 100
        channel._remote_window_start = 100
        channel._remote_sequence = 105

        # Try to send old packet (seq 90)
        packet = NetPacket(PacketProperty.CHANNELED, 10)
        packet.sequence = 90
        packet.channel_id = 0

        result = channel.process_packet(packet)
        assert result is False  # Should be rejected


class TestChannelErrors:
    """Test error handling / 测试错误处理"""

    def test_packet_too_far_ahead(self):
        """Test packet too far ahead is rejected / 测试超前的数据包被拒绝"""
        peer = MockPeer()
        channel = ReliableChannel(peer, ordered=True, channel_id=0)

        channel._remote_sequence = 0

        # Try to send packet way beyond window size
        packet = NetPacket(PacketProperty.CHANNELED, 10)
        packet.sequence = NetConstants.DEFAULT_WINDOW_SIZE * 2 + 10
        packet.channel_id = 0

        result = channel.process_packet(packet)
        assert result is False

    def test_invalid_ack_packet(self):
        """Test invalid ACK packet handling / 测试无效 ACK 包处理"""
        peer = MockPeer()
        channel = ReliableChannel(peer, ordered=True, channel_id=0)

        # Create ACK packet with wrong size
        ack_packet = NetPacket(PacketProperty.ACK, 10)
        ack_packet.size = 5  # Wrong size

        # Should not crash
        result = channel.process_packet(ack_packet)
        assert result is False

    def test_ack_beyond_window(self):
        """Test ACK beyond window / 测试超出窗口的 ACK"""
        peer = MockPeer()
        channel = ReliableChannel(peer, ordered=True, channel_id=0)

        # Send packet
        packet = NetPacket(PacketProperty.CHANNELED, 10)
        channel.add_to_queue(packet)
        channel.send_next_packets()

        # Create ACK with sequence beyond window
        ack_packet = NetPacket(PacketProperty.ACK, channel._outgoing_acks.size)
        ack_packet.sequence = NetConstants.MAX_SEQUENCE  # Way beyond
        ack_packet.channel_id = 0

        # Should be ignored
        result = channel.process_packet(ack_packet)
        assert result is False


class TestChannelEdgeCases:
    """Test edge cases / 测试边界情况"""

    def test_empty_packet_processing(self):
        """Test processing empty packet / 测试处理空数据包"""
        peer = MockPeer()
        channel = ReliableChannel(peer, ordered=True, channel_id=0)

        packet = NetPacket(PacketProperty.CHANNELED, 0)
        packet.sequence = 0
        packet.channel_id = 0

        result = channel.process_packet(packet)
        assert result is True

    def test_channel_with_different_ids(self):
        """Test channels with different IDs / 测试不同 ID 的通道"""
        peer = MockPeer()

        for channel_id in range(4):
            channel = ReliableChannel(peer, ordered=True, channel_id=channel_id)
            assert channel._id == channel_id
            assert channel._outgoing_acks.channel_id == channel_id

    def test_window_size_boundary(self):
        """Test at window size boundary / 测试窗口大小边界"""
        peer = MockPeer()
        channel = ReliableChannel(peer, ordered=True, channel_id=0)

        # Send exactly window_size packets
        for i in range(NetConstants.DEFAULT_WINDOW_SIZE):
            packet = NetPacket(PacketProperty.CHANNELED, 10)
            channel.add_to_queue(packet)

        result = channel.send_next_packets()
        # Some packets should be sent
        assert len(peer.sent_packets) > 0


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
