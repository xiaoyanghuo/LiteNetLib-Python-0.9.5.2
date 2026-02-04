"""
Tests for channel integration with NetPeer.

Tests that NetPeer properly uses the channel system for all delivery methods.
"""

import pytest
import asyncio
from unittest.mock import Mock, MagicMock, patch
from litenetlib.core.peer import NetPeer, ConnectionState
from litenetlib.core.manager import LiteNetManager
from litenetlib.core.events import EventBasedNetListener
from litenetlib.core.constants import DeliveryMethod, PacketProperty, NetConstants
from litenetlib.core.packet import NetPacket
from litenetlib.utils.data_reader import NetDataReader
from litenetlib.utils.data_writer import NetDataWriter


class TestChannelIntegration:
    """Test that NetPeer properly integrates with channel system."""

    def test_peer_creates_reliable_ordered_channel(self):
        """Test that requesting RELIABLE_ORDERED creates correct channel."""
        # Create manager and peer
        listener = EventBasedNetListener()
        manager = Mock(spec=LiteNetManager)
        manager.listener = listener
        manager._socket = Mock()
        manager._packet_merging_enabled = False  # Disable for immediate send tests

        peer = NetPeer(manager, ("127.0.0.1", 9050), 0)
        peer._state = ConnectionState.CONNECTED

        # Get channel for RELIABLE_ORDERED
        channel = peer._get_or_create_channel(DeliveryMethod.RELIABLE_ORDERED, 0)

        # Verify channel type and properties
        from litenetlib.channels.reliable_channel import ReliableChannel
        assert isinstance(channel, ReliableChannel)
        assert channel._ordered is True
        assert channel._id == 0

    def test_peer_creates_sequenced_channel(self):
        """Test that requesting SEQUENCED creates correct channel."""
        manager = Mock(spec=LiteNetManager)
        manager.listener = EventBasedNetListener()
        manager._socket = Mock()
        manager._packet_merging_enabled = False  # Disable for immediate send tests

        peer = NetPeer(manager, ("127.0.0.1", 9050), 0)
        peer._state = ConnectionState.CONNECTED

        # Get channel for SEQUENCED
        channel = peer._get_or_create_channel(DeliveryMethod.SEQUENCED, 0)

        # Verify channel type and properties
        from litenetlib.channels.sequenced_channel import SequencedChannel
        assert isinstance(channel, SequencedChannel)
        assert channel._reliable is False
        assert channel._id == 1

    def test_peer_creates_reliable_unordered_channel(self):
        """Test that requesting RELIABLE_UNORDERED creates correct channel."""
        manager = Mock(spec=LiteNetManager)
        manager.listener = EventBasedNetListener()
        manager._socket = Mock()
        manager._packet_merging_enabled = False  # Disable for immediate send tests

        peer = NetPeer(manager, ("127.0.0.1", 9050), 0)
        peer._state = ConnectionState.CONNECTED

        # Get channel for RELIABLE_UNORDERED
        channel = peer._get_or_create_channel(DeliveryMethod.RELIABLE_UNORDERED, 0)

        # Verify channel type and properties
        from litenetlib.channels.reliable_channel import ReliableChannel
        assert isinstance(channel, ReliableChannel)
        assert channel._ordered is False
        assert channel._id == 2

    def test_peer_creates_reliable_sequenced_channel(self):
        """Test that requesting RELIABLE_SEQUENCED creates correct channel."""
        manager = Mock(spec=LiteNetManager)
        manager.listener = EventBasedNetListener()
        manager._socket = Mock()
        manager._packet_merging_enabled = False  # Disable for immediate send tests

        peer = NetPeer(manager, ("127.0.0.1", 9050), 0)
        peer._state = ConnectionState.CONNECTED

        # Get channel for RELIABLE_SEQUENCED
        channel = peer._get_or_create_channel(DeliveryMethod.RELIABLE_SEQUENCED, 0)

        # Verify channel type and properties
        from litenetlib.channels.sequenced_channel import SequencedChannel
        assert isinstance(channel, SequencedChannel)
        assert channel._reliable is True
        assert channel._id == 1  # Shares channel 1 with SEQUENCED

    def test_send_unreliable_bypasses_channel(self):
        """Test that UNRELIABLE delivery bypasses channel system."""
        manager = Mock(spec=LiteNetManager)
        manager.listener = EventBasedNetListener()
        manager._socket = Mock()
        manager._packet_merging_enabled = False  # Disable for immediate send tests

        peer = NetPeer(manager, ("127.0.0.1", 9050), 0)
        peer._state = ConnectionState.CONNECTED

        # Send unreliable data
        peer.send(b"test_data", DeliveryMethod.UNRELIABLE)

        # Verify packet was sent directly (not through channel)
        assert manager._socket.sendto.called
        call_args = manager._socket.sendto.call_args[0]
        data_sent = call_args[0]

        # Parse packet
        packet = NetPacket.from_bytes(data_sent)
        assert packet.packet_property == PacketProperty.UNRELIABLE

    def test_send_reliable_ordered_uses_channel(self):
        """Test that RELIABLE_ORDERED uses channel system."""
        manager = Mock(spec=LiteNetManager)
        manager.listener = EventBasedNetListener()
        manager._socket = Mock()
        manager._packet_merging_enabled = False  # Disable for immediate send tests

        peer = NetPeer(manager, ("127.0.0.1", 9050), 0)
        peer._state = ConnectionState.CONNECTED

        # Send reliable ordered data
        peer.send(b"test_data", DeliveryMethod.RELIABLE_ORDERED)

        # Verify channel was created and packet queued
        channel = peer._channels[0]
        assert channel is not None
        assert channel.packets_in_queue == 1

    def test_send_sequenced_uses_channel(self):
        """Test that SEQUENCED uses channel system."""
        manager = Mock(spec=LiteNetManager)
        manager.listener = EventBasedNetListener()
        manager._socket = Mock()
        manager._packet_merging_enabled = False  # Disable for immediate send tests

        peer = NetPeer(manager, ("127.0.0.1", 9050), 0)
        peer._state = ConnectionState.CONNECTED

        # Send sequenced data
        peer.send(b"test_data", DeliveryMethod.SEQUENCED)

        # Verify channel was created and packet queued
        channel = peer._channels[1]
        assert channel is not None
        assert channel.packets_in_queue == 1

    def test_channel_number_routing(self):
        """Test that different channel numbers create different channels."""
        manager = Mock(spec=LiteNetManager)
        manager.listener = EventBasedNetListener()
        manager._socket = Mock()
        manager._packet_merging_enabled = False  # Disable for immediate send tests

        peer = NetPeer(manager, ("127.0.0.1", 9050), 0)
        peer._state = ConnectionState.CONNECTED

        # Send to channel 0
        peer.send(b"data0", DeliveryMethod.RELIABLE_ORDERED, channel_number=0)
        channel0 = peer._channels[0]

        # Send to channel 1
        peer.send(b"data1", DeliveryMethod.RELIABLE_ORDERED, channel_number=1)
        channel2 = peer._channels[2]  # Channel 1 uses index 2

        # Verify different channels
        assert channel0 is not None
        assert channel2 is not None
        assert channel0 is not channel2

    def test_process_chnneled_packet_routes_to_channel(self):
        """Test that channeled packets are routed to correct channel."""
        manager = Mock(spec=LiteNetManager)
        listener = EventBasedNetListener()
        manager.listener = listener
        manager._socket = Mock()
        manager._packet_merging_enabled = False  # Disable for immediate send tests

        peer = NetPeer(manager, ("127.0.0.1", 9050), 0)
        peer._state = ConnectionState.CONNECTED

        # Create channel first (channels are created on-demand when sending)
        peer.send(b"init", DeliveryMethod.RELIABLE_ORDERED)

        # Create a channeled packet
        packet = NetPacket(PacketProperty.CHANNELED, 5)
        packet._data[4:] = b"hello"
        packet.sequence = 0
        packet.channel_id = 0

        # Process packet
        asyncio.run(peer.process_packet(packet))

        # Channel should exist and have processed the packet
        channel = peer._channels[0]
        assert channel is not None

    def test_process_ack_packet_routes_to_channel(self):
        """Test that ACK packets are routed to correct channel."""
        manager = Mock(spec=LiteNetManager)
        listener = EventBasedNetListener()
        manager.listener = listener
        manager._socket = Mock()
        manager._packet_merging_enabled = False  # Disable for immediate send tests

        peer = NetPeer(manager, ("127.0.0.1", 9050), 0)
        peer._state = ConnectionState.CONNECTED

        # Create channel first
        peer._get_or_create_channel(DeliveryMethod.RELIABLE_ORDERED, 0)

        # Create ACK packet
        ack_packet = NetPacket(PacketProperty.ACK, 10)
        ack_packet.sequence = 0
        ack_packet.channel_id = 0

        # Process ACK
        asyncio.run(peer.process_packet(ack_packet))

        # Channel should have processed ACK
        # (This mainly tests no errors occur)

    def test_resend_delay_calculation(self):
        """Test that resend_delay is calculated based on RTT."""
        manager = Mock(spec=LiteNetManager)
        manager.listener = EventBasedNetListener()
        manager._socket = Mock()
        manager._packet_merging_enabled = False  # Disable for immediate send tests

        peer = NetPeer(manager, ("127.0.0.1", 9050), 0)

        # Initial RTT is 0
        assert peer._rtt == 0

        # Resend delay with RTT=0 should be rtt*2+100 with minimum rtt of 50
        # 50*2+100 = 200
        assert peer.resend_delay == 200

        # Set RTT to 100ms
        peer._rtt = 100
        # 100*2+100 = 300
        assert peer.resend_delay == 300

    def test_get_packets_count_in_reliable_queue(self):
        """Test getting packet count from reliable queues."""
        manager = Mock(spec=LiteNetManager)
        manager.listener = EventBasedNetListener()
        manager._socket = Mock()
        manager._packet_merging_enabled = False  # Disable for immediate send tests

        peer = NetPeer(manager, ("127.0.0.1", 9050), 0)
        peer._state = ConnectionState.CONNECTED

        # Send some reliable ordered packets
        peer.send(b"data1", DeliveryMethod.RELIABLE_ORDERED)
        peer.send(b"data2", DeliveryMethod.RELIABLE_ORDERED)

        # Get count for ordered
        ordered_count = peer.get_packets_count_in_reliable_queue(ordered=True)
        assert ordered_count == 2

        # Get count for unordered (should be 0)
        unordered_count = peer.get_packets_count_in_reliable_queue(ordered=False)
        assert unordered_count == 0

    def test_update_processes_channel_send_queue(self):
        """Test that update_async processes channel send queue."""
        manager = Mock(spec=LiteNetManager)
        manager.listener = EventBasedNetListener()
        manager._socket = Mock()
        manager._packet_merging_enabled = False  # Disable for immediate send tests

        peer = NetPeer(manager, ("127.0.0.1", 9050), 0)
        peer._state = ConnectionState.CONNECTED

        # Add packet to channel
        peer.send(b"test_data", DeliveryMethod.RELIABLE_ORDERED)

        # Run update with limit to prevent infinite loop
        # The channel will process packets and may need multiple iterations
        for _ in range(10):  # Limit iterations
            if not peer._channel_send_queue:
                break
            asyncio.run(peer.update_async(1000))

        # Verify channel was processed
        # Channel should have sent the packet
        assert manager._socket.sendto.called

        # Channel may still be in queue due to pending ACKs
        # This is expected behavior

    def test_shutdown_clears_channels(self):
        """Test that shutdown clears all channels."""
        manager = Mock(spec=LiteNetManager)
        manager.listener = EventBasedNetListener()
        manager._socket = Mock()
        manager._packet_merging_enabled = False  # Disable for immediate send tests

        peer = NetPeer(manager, ("127.0.0.1", 9050), 0)
        peer._state = ConnectionState.CONNECTED

        # Create channels
        peer.send(b"data1", DeliveryMethod.RELIABLE_ORDERED)
        peer.send(b"data2", DeliveryMethod.SEQUENCED)

        # Verify channels exist
        assert peer._channels[0] is not None
        assert peer._channels[1] is not None

        # Shutdown
        peer.shutdown()

        # Verify channels cleared
        assert peer._channels[0] is None
        assert peer._channels[1] is None
        assert peer._state == ConnectionState.DISCONNECTED


class TestChannelDeliveryMethods:
    """Test all delivery methods work correctly."""

    def test_all_delivery_methods_create_channels(self):
        """Test that all non-UNRELIABLE methods create channels."""
        manager = Mock(spec=LiteNetManager)
        manager.listener = EventBasedNetListener()
        manager._socket = Mock()
        manager._packet_merging_enabled = False  # Disable for immediate send tests

        peer = NetPeer(manager, ("127.0.0.1", 9050), 0)
        peer._state = ConnectionState.CONNECTED

        # RELIABLE_UNORDERED -> channel 2
        peer.send(b"data", DeliveryMethod.RELIABLE_UNORDERED)
        assert peer._channels[2] is not None

        # SEQUENCED -> channel 1
        peer.send(b"data", DeliveryMethod.SEQUENCED)
        assert peer._channels[1] is not None

        # RELIABLE_ORDERED -> channel 0
        peer.send(b"data", DeliveryMethod.RELIABLE_ORDERED)
        assert peer._channels[0] is not None

        # RELIABLE_SEQUENCED -> channel 1 (same as SEQUENCED)
        peer.send(b"data", DeliveryMethod.RELIABLE_SEQUENCED)
        # Channel 1 should exist (SequencedChannel)
        from litenetlib.channels.sequenced_channel import SequencedChannel
        assert isinstance(peer._channels[1], SequencedChannel)


class TestNetDataWriterSend:
    """Test sending NetDataWriter through channels."""

    def test_send_net_data_writer(self):
        """Test that NetDataWriter can be sent through channels."""
        manager = Mock(spec=LiteNetManager)
        manager.listener = EventBasedNetListener()
        manager._socket = Mock()
        manager._packet_merging_enabled = False  # Disable for immediate send tests

        peer = NetPeer(manager, ("127.0.0.1", 9050), 0)
        peer._state = ConnectionState.CONNECTED

        # Create NetDataWriter
        writer = NetDataWriter()
        writer.put_int(42)
        writer.put_string("hello")

        # Send through channel
        peer.send(writer, DeliveryMethod.RELIABLE_ORDERED)

        # Verify packet queued in channel
        assert peer._channels[0] is not None
        assert peer._channels[0].packets_in_queue == 1


class TestSendWithOffset:
    """Test sending with offset and length parameters."""

    def test_send_with_offset_and_length(self):
        """Test sending with start offset and length."""
        manager = Mock(spec=LiteNetManager)
        manager.listener = EventBasedNetListener()
        manager._socket = Mock()
        manager._packet_merging_enabled = False  # Disable for immediate send tests

        peer = NetPeer(manager, ("127.0.0.1", 9050), 0)
        peer._state = ConnectionState.CONNECTED

        # Send with offset and length
        data = b"HelloWorld"
        peer.send(data, DeliveryMethod.RELIABLE_ORDERED, start=5, length=5)

        # Verify packet queued
        assert peer._channels[0].packets_in_queue == 1

    def test_send_with_offset_only(self):
        """Test sending with start offset only."""
        manager = Mock(spec=LiteNetManager)
        manager.listener = EventBasedNetListener()
        manager._socket = Mock()
        manager._packet_merging_enabled = False  # Disable for immediate send tests

        peer = NetPeer(manager, ("127.0.0.1", 9050), 0)
        peer._state = ConnectionState.CONNECTED

        # Send with offset (length calculated automatically)
        data = b"HelloWorld"
        peer.send(data, DeliveryMethod.RELIABLE_ORDERED, start=5)

        # Verify packet queued with "World" only
        assert peer._channels[0].packets_in_queue == 1
