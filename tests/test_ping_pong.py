"""
Tests for Ping/Pong functionality.

Tests ping sending, pong handling, RTT calculation, and timeout.
"""

import pytest
import time
import asyncio
from unittest.mock import Mock, MagicMock, patch
from litenetlib.core.peer import NetPeer, ConnectionState
from litenetlib.core.manager import LiteNetManager
from litenetlib.core.events import EventBasedNetListener
from litenetlib.core.constants import PacketProperty, DeliveryMethod, DisconnectReason
from litenetlib.core.packet import NetPacket
from litenetlib.utils.net_utils import NetUtils


def run_async(coro):
    """Helper to run async functions in tests."""
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    return loop.run_until_complete(coro)


class TestSendPing:
    """Test send_ping method."""

    def test_send_ping_creates_packet(self):
        """Test that send_ping creates a ping packet."""
        manager = Mock(spec=LiteNetManager)
        manager.listener = EventBasedNetListener()
        manager._socket = Mock()
        manager._mtu_discovery = False
        manager._packet_merging_enabled = False

        peer = NetPeer(manager, ("127.0.0.1", 9050), 0)
        peer._state = ConnectionState.CONNECTED
        peer._last_receive_time = NetUtils.get_time_millis()

        # Mock _send_raw to capture packet
        sent_packets = []
        def mock_send_raw(packet):
            sent_packets.append(packet)

        peer._send_raw = mock_send_raw

        # Send ping
        peer.send_ping()

        # Verify ping packet was sent
        assert len(sent_packets) == 1
        assert sent_packets[0].packet_property == PacketProperty.PING

    def test_send_ping_records_time(self):
        """Test that send_ping records send time."""
        manager = Mock(spec=LiteNetManager)
        manager.listener = EventBasedNetListener()
        manager._socket = Mock()
        manager._mtu_discovery = False
        manager._packet_merging_enabled = False

        peer = NetPeer(manager, ("127.0.0.1", 9050), 0)
        peer._state = ConnectionState.CONNECTED

        before_time = NetUtils.get_time_millis()

        peer._send_raw = Mock()  # Mock send to avoid actual send
        peer.send_ping()

        after_time = NetUtils.get_time_millis()

        # Verify ping_send_time was set
        assert peer._ping_send_time >= before_time
        assert peer._ping_send_time <= after_time
        assert peer._last_ping_send_time >= before_time
        assert peer._last_ping_send_time <= after_time

    def test_send_ping_increments_attempts(self):
        """Test that send_ping increments attempt counter."""
        manager = Mock(spec=LiteNetManager)
        manager.listener = EventBasedNetListener()
        manager._socket = Mock()
        manager._mtu_discovery = False
        manager._packet_merging_enabled = False

        peer = NetPeer(manager, ("127.0.0.1", 9050), 0)
        peer._state = ConnectionState.CONNECTED
        peer._ping_attempts = 0

        peer._send_raw = Mock()

        # Send multiple pings
        peer.send_ping()
        assert peer._ping_attempts == 1

        peer.send_ping()
        assert peer._ping_attempts == 2

        peer.send_ping()
        assert peer._ping_attempts == 3


class TestHandlePong:
    """Test _handle_pong method."""

    def test_handle_pong_calculates_rtt(self):
        """Test that pong calculates RTT correctly."""
        manager = Mock(spec=LiteNetManager)
        manager.listener = EventBasedNetListener()
        manager._socket = Mock()
        manager._mtu_discovery = False
        manager._packet_merging_enabled = False

        peer = NetPeer(manager, ("127.0.0.1", 9050), 0)
        peer._state = ConnectionState.CONNECTED

        # Set initial RTT to avoid weighted average affecting first measurement
        peer._rtt = 100

        # Simulate ping sent 100ms ago
        peer._ping_send_time = NetUtils.get_time_millis() - 100

        # Create and handle pong
        pong = NetPacket(PacketProperty.PONG, 4)
        run_async(peer._handle_pong(pong))

        # RTT should be approximately 100ms (weighted average: (3*100 + 100)/4 = 100)
        assert peer._rtt >= 90  # Allow some variance
        assert peer._rtt <= 150

    def test_handle_pong_uses_weighted_average(self):
        """Test that RTT uses weighted average (3 * old + new) / 4."""
        manager = Mock(spec=LiteNetManager)
        manager.listener = EventBasedNetListener()
        manager._socket = Mock()
        manager._mtu_discovery = False
        manager._packet_merging_enabled = False

        peer = NetPeer(manager, ("127.0.0.1", 9050), 0)
        peer._state = ConnectionState.CONNECTED

        # Set initial RTT
        peer._rtt = 100

        # Simulate ping with new RTT of 200ms
        peer._ping_send_time = NetUtils.get_time_millis() - 200

        pong = NetPacket(PacketProperty.PONG, 4)
        run_async(peer._handle_pong(pong))

        # New RTT should be (3 * 100 + 200) / 4 = 125
        assert peer._rtt == 125

    def test_handle_pong_resets_attempts(self):
        """Test that receiving pong resets ping attempts."""
        manager = Mock(spec=LiteNetManager)
        manager.listener = EventBasedNetListener()
        manager._socket = Mock()
        manager._mtu_discovery = False
        manager._packet_merging_enabled = False

        peer = NetPeer(manager, ("127.0.0.1", 9050), 0)
        peer._state = ConnectionState.CONNECTED
        peer._ping_attempts = 3
        peer._ping_send_time = NetUtils.get_time_millis() - 50

        pong = NetPacket(PacketProperty.PONG, 4)
        run_async(peer._handle_pong(pong))

        # Attempts should be reset
        assert peer._ping_attempts == 0
        assert peer._ping_send_time == 0

    def test_handle_pong_triggers_latency_event(self):
        """Test that pong triggers latency update event."""
        listener = EventBasedNetListener()
        manager = Mock(spec=LiteNetManager)
        manager.listener = listener
        manager._socket = Mock()
        manager._mtu_discovery = False
        manager._packet_merging_enabled = False

        peer = NetPeer(manager, ("127.0.0.1", 9050), 0)
        peer._state = ConnectionState.CONNECTED
        peer._ping_send_time = NetUtils.get_time_millis() - 100

        # Track latency updates
        latency_updates = []
        def on_latency_update(peer, rtt):
            latency_updates.append((peer, rtt))

        listener.set_network_latency_update_callback(on_latency_update)

        pong = NetPacket(PacketProperty.PONG, 4)
        run_async(peer._handle_pong(pong))

        # Should have triggered latency update
        assert len(latency_updates) == 1
        assert latency_updates[0][0] == peer
        assert latency_updates[0][1] == peer._rtt


class TestHandlePing:
    """Test _handle_ping method."""

    def test_handle_ping_sends_pong(self):
        """Test that receiving ping sends pong response."""
        manager = Mock(spec=LiteNetManager)
        manager.listener = EventBasedNetListener()
        manager._socket = Mock()
        manager._mtu_discovery = False
        manager._packet_merging_enabled = False

        peer = NetPeer(manager, ("127.0.0.1", 9050), 0)
        peer._state = ConnectionState.CONNECTED

        # Track sent packets
        sent_packets = []
        def mock_send_raw(packet):
            sent_packets.append(packet)

        peer._send_raw = mock_send_raw

        # Receive ping
        ping = NetPacket(PacketProperty.PING, 4)
        run_async(peer._handle_ping(ping))

        # Should send pong
        assert len(sent_packets) == 1
        assert sent_packets[0].packet_property == PacketProperty.PONG


class TestUpdateAsyncPing:
    """Test ping logic in update_async."""

    def test_update_sends_ping_when_idle(self):
        """Test that update sends ping when connection is idle."""
        manager = Mock(spec=LiteNetManager)
        manager.listener = EventBasedNetListener()
        manager._socket = Mock()
        manager._mtu_discovery = False
        manager._packet_merging_enabled = False

        peer = NetPeer(manager, ("127.0.0.1", 9050), 0)
        peer._state = ConnectionState.CONNECTED

        # Set last receive time to past
        current_time = NetUtils.get_time_millis()
        peer._last_receive_time = current_time - 2000  # 2 seconds ago
        peer._last_ping_send_time = current_time - 2000  # 2 seconds ago

        # Mock send_ping
        ping_sent = []
        def mock_send_ping():
            ping_sent.append(True)

        peer.send_ping = mock_send_ping

        # Update with time past ping interval
        run_async(peer.update_async(current_time))

        # Should have sent ping
        assert len(ping_sent) == 1

    def test_update_does_not_send_ping_when_receiving_data(self):
        """Test that update doesn't send ping when actively receiving data."""
        manager = Mock(spec=LiteNetManager)
        manager.listener = EventBasedNetListener()
        manager._socket = Mock()
        manager._mtu_discovery = False
        manager._packet_merging_enabled = False

        peer = NetPeer(manager, ("127.0.0.1", 9050), 0)
        peer._state = ConnectionState.CONNECTED

        # Set last receive time to recent
        current_time = NetUtils.get_time_millis()
        peer._last_receive_time = current_time - 100  # 100ms ago
        peer._last_ping_send_time = current_time - 2000  # 2 seconds ago

        # Mock send_ping
        ping_sent = []
        def mock_send_ping():
            ping_sent.append(True)

        peer.send_ping = mock_send_ping

        # Update
        run_async(peer.update_async(current_time))

        # Should NOT have sent ping (actively receiving data)
        assert len(ping_sent) == 0

    def test_update_disconnects_on_max_ping_attempts(self):
        """Test that peer disconnects after max failed ping attempts."""
        listener = EventBasedNetListener()
        manager = Mock(spec=LiteNetManager)
        manager.listener = listener
        manager._socket = Mock()
        manager._mtu_discovery = False
        manager._packet_merging_enabled = False

        peer = NetPeer(manager, ("127.0.0.1", 9050), 0)
        peer._state = ConnectionState.CONNECTED

        # Track disconnect events
        disconnects = []
        def on_disconnect(peer, reason):
            disconnects.append((peer, reason))

        listener.set_peer_disconnected_callback(on_disconnect)

        # Set ping attempts to max
        peer._ping_attempts = peer._max_ping_attempts
        peer._last_receive_time = NetUtils.get_time_millis() - 10000  # Long time ago

        # Update
        run_async(peer.update_async(NetUtils.get_time_millis()))

        # Should have disconnected
        assert peer._state == ConnectionState.DISCONNECTED
        assert len(disconnects) == 1
        assert disconnects[0][1] == DisconnectReason.TIMEOUT


class TestPingPongIntegration:
    """Integration tests for ping/pong mechanism."""

    def test_ping_pong_round_trip(self):
        """Test complete ping/pong round trip."""
        # Create two peers
        manager1 = Mock(spec=LiteNetManager)
        manager1.listener = EventBasedNetListener()
        manager1._socket = Mock()
        manager1._mtu_discovery = False
        manager1._packet_merging_enabled = False

        manager2 = Mock(spec=LiteNetManager)
        manager2.listener = EventBasedNetListener()
        manager2._socket = Mock()
        manager2._mtu_discovery = False
        manager2._packet_merging_enabled = False

        peer1 = NetPeer(manager1, ("127.0.0.1", 9050), 0)
        peer1._state = ConnectionState.CONNECTED

        peer2 = NetPeer(manager2, ("127.0.0.1", 9051), 0)
        peer2._state = ConnectionState.CONNECTED

        # Capture packets sent by peer1
        peer1_packets = []
        def peer1_send(packet):
            peer1_packets.append(packet)

        peer1._send_raw = peer1_send

        # Peer1 sends ping
        peer1.send_ping()

        # Verify ping packet
        assert len(peer1_packets) == 1
        ping_packet = peer1_packets[0]
        assert ping_packet.packet_property == PacketProperty.PING

        # Simulate time delay for RTT calculation by manually adjusting ping_send_time
        # This ensures RTT calculation is not affected by timing precision
        peer1._ping_send_time = NetUtils.get_time_millis() - 50  # 50ms ago

        # Peer2 receives ping and sends pong
        peer2_packets = []
        def peer2_send(packet):
            peer2_packets.append(packet)

        peer2._send_raw = peer2_send
        run_async(peer2._handle_ping(ping_packet))

        # Verify pong packet
        assert len(peer2_packets) == 1
        pong_packet = peer2_packets[0]
        assert pong_packet.packet_property == PacketProperty.PONG

        # Peer1 receives pong
        run_async(peer1._handle_pong(pong_packet))

        # Verify RTT was calculated (should be at least 1ms)
        assert peer1._rtt > 0
        assert peer1.ping > 0


class TestEdgeCases:
    """Test edge cases and error conditions."""

    def test_handle_pong_without_ping(self):
        """Test handling pong without corresponding ping."""
        manager = Mock(spec=LiteNetManager)
        manager.listener = EventBasedNetListener()
        manager._socket = Mock()
        manager._mtu_discovery = False
        manager._packet_merging_enabled = False

        peer = NetPeer(manager, ("127.0.0.1", 9050), 0)
        peer._state = ConnectionState.CONNECTED
        peer._ping_send_time = 0  # No ping sent

        pong = NetPacket(PacketProperty.PONG, 4)
        run_async(peer._handle_pong(pong))

        # Should not crash or update RTT
        assert peer._rtt == 0

    def test_ping_property_calculated_from_rtt(self):
        """Test that ping property is RTT / 2."""
        manager = Mock(spec=LiteNetManager)
        manager.listener = EventBasedNetListener()
        manager._socket = Mock()
        manager._mtu_discovery = False
        manager._packet_merging_enabled = False

        peer = NetPeer(manager, ("127.0.0.1", 9050), 0)
        peer._state = ConnectionState.CONNECTED

        # Set RTT to 100ms
        peer._rtt = 100

        # Ping should be RTT / 2
        assert peer.ping == 50
