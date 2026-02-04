"""
Tests for NetStatistics class.

Tests all properties and methods of the network statistics tracking class.
"""

import pytest
from litenetlib.core.statistics import NetStatistics


class TestNetStatisticsCreation:
    """Test NetStatistics object creation and initial state."""

    def test_statistics_creation(self):
        """Test creating a new NetStatistics object."""
        stats = NetStatistics()
        assert stats.packets_sent == 0
        assert stats.packets_received == 0
        assert stats.bytes_sent == 0
        assert stats.bytes_received == 0
        assert stats.packet_loss == 0
        assert stats.packet_loss_percent == 0.0


class TestPacketsSent:
    """Test packets sent tracking."""

    def test_initial_packets_sent(self):
        """Test initial packets sent is zero."""
        stats = NetStatistics()
        assert stats.packets_sent == 0

    def test_increment_packets_sent(self):
        """Test incrementing packets sent."""
        stats = NetStatistics()
        stats.increment_packets_sent()
        assert stats.packets_sent == 1
        stats.increment_packets_sent()
        assert stats.packets_sent == 2

    def test_increment_multiple_times(self):
        """Test incrementing packets sent multiple times."""
        stats = NetStatistics()
        for _ in range(100):
            stats.increment_packets_sent()
        assert stats.packets_sent == 100


class TestPacketsReceived:
    """Test packets received tracking."""

    def test_initial_packets_received(self):
        """Test initial packets received is zero."""
        stats = NetStatistics()
        assert stats.packets_received == 0

    def test_increment_packets_received(self):
        """Test incrementing packets received."""
        stats = NetStatistics()
        stats.increment_packets_received()
        assert stats.packets_received == 1
        stats.increment_packets_received()
        assert stats.packets_received == 2

    def test_increment_multiple_times(self):
        """Test incrementing packets received multiple times."""
        stats = NetStatistics()
        for _ in range(50):
            stats.increment_packets_received()
        assert stats.packets_received == 50


class TestBytesSent:
    """Test bytes sent tracking."""

    def test_initial_bytes_sent(self):
        """Test initial bytes sent is zero."""
        stats = NetStatistics()
        assert stats.bytes_sent == 0

    def test_add_bytes_sent(self):
        """Test adding bytes sent."""
        stats = NetStatistics()
        stats.add_bytes_sent(1024)
        assert stats.bytes_sent == 1024
        stats.add_bytes_sent(2048)
        assert stats.bytes_sent == 3072

    def test_add_large_bytes_sent(self):
        """Test adding large number of bytes sent."""
        stats = NetStatistics()
        stats.add_bytes_sent(1024 * 1024)  # 1 MB
        assert stats.bytes_sent == 1048576

    def test_add_zero_bytes_sent(self):
        """Test adding zero bytes sent."""
        stats = NetStatistics()
        stats.add_bytes_sent(0)
        assert stats.bytes_sent == 0


class TestBytesReceived:
    """Test bytes received tracking."""

    def test_initial_bytes_received(self):
        """Test initial bytes received is zero."""
        stats = NetStatistics()
        assert stats.bytes_received == 0

    def test_add_bytes_received(self):
        """Test adding bytes received."""
        stats = NetStatistics()
        stats.add_bytes_received(512)
        assert stats.bytes_received == 512
        stats.add_bytes_received(256)
        assert stats.bytes_received == 768

    def test_add_large_bytes_received(self):
        """Test adding large number of bytes received."""
        stats = NetStatistics()
        stats.add_bytes_received(10 * 1024 * 1024)  # 10 MB
        assert stats.bytes_received == 10485760


class TestPacketLoss:
    """Test packet loss tracking."""

    def test_initial_packet_loss(self):
        """Test initial packet loss is zero."""
        stats = NetStatistics()
        assert stats.packet_loss == 0

    def test_increment_packet_loss(self):
        """Test incrementing packet loss."""
        stats = NetStatistics()
        stats.increment_packet_loss()
        assert stats.packet_loss == 1
        stats.increment_packet_loss()
        assert stats.packet_loss == 2

    def test_add_packet_loss(self):
        """Test adding packet loss."""
        stats = NetStatistics()
        stats.add_packet_loss(5)
        assert stats.packet_loss == 5
        stats.add_packet_loss(3)
        assert stats.packet_loss == 8


class TestPacketLossPercent:
    """Test packet loss percentage calculation."""

    def test_packet_loss_percent_no_loss(self):
        """Test packet loss percent with no loss."""
        stats = NetStatistics()
        stats.increment_packets_sent()
        assert stats.packet_loss_percent == 0.0

    def test_packet_loss_percent_with_loss(self):
        """Test packet loss percent with loss."""
        stats = NetStatistics()
        stats.increment_packets_sent()
        stats.increment_packet_loss()
        # 1 loss out of 2 total = 50%
        assert stats.packet_loss_percent == 50.0

    def test_packet_loss_percent_multiple(self):
        """Test packet loss percent with multiple packets."""
        stats = NetStatistics()
        for _ in range(90):
            stats.increment_packets_sent()
        for _ in range(10):
            stats.increment_packet_loss()
        # 10 loss out of 100 total = 10%
        assert stats.packet_loss_percent == 10.0

    def test_packet_loss_percent_zero_total(self):
        """Test packet loss percent when no packets sent."""
        stats = NetStatistics()
        assert stats.packet_loss_percent == 0.0


class TestReset:
    """Test reset functionality."""

    def test_reset_all_values(self):
        """Test resetting all statistics to zero."""
        stats = NetStatistics()
        # Set some values
        stats.increment_packets_sent()
        stats.increment_packets_received()
        stats.add_bytes_sent(1000)
        stats.add_bytes_received(2000)
        stats.increment_packet_loss()

        # Reset
        stats.reset()

        # Check all zero
        assert stats.packets_sent == 0
        assert stats.packets_received == 0
        assert stats.bytes_sent == 0
        assert stats.bytes_received == 0
        assert stats.packet_loss == 0
        assert stats.packet_loss_percent == 0.0


class TestStringRepresentation:
    """Test string representation of statistics."""

    def test_str_representation(self):
        """Test __str__ method."""
        stats = NetStatistics()
        stats.increment_packets_sent()
        stats.increment_packets_received()
        stats.add_bytes_sent(1024)
        stats.add_bytes_received(2048)
        stats.increment_packet_loss()

        str_repr = str(stats)
        assert "NetStatistics" in str_repr
        assert "sent=1" in str_repr
        assert "received=1" in str_repr
        assert "bytes_sent=1024" in str_repr
        assert "bytes_received=2048" in str_repr
        assert "loss=1" in str_repr

    def test_repr_method(self):
        """Test __repr__ method."""
        stats = NetStatistics()
        stats.increment_packets_sent()
        repr_str = repr(stats)
        assert "NetStatistics" in repr_str


class TestComprehensiveScenario:
    """Test comprehensive real-world scenarios."""

    def test_network_session(self):
        """Test simulating a network session."""
        stats = NetStatistics()

        # Send 1000 packets
        for _ in range(1000):
            stats.increment_packets_sent()
        stats.add_bytes_sent(1000 * 1024)  # ~1KB per packet

        # Receive 950 packets
        for _ in range(950):
            stats.increment_packets_received()
        stats.add_bytes_received(950 * 512)  # ~512B per packet

        # 50 packets lost
        stats.add_packet_loss(50)

        # Verify
        assert stats.packets_sent == 1000
        assert stats.packets_received == 950
        assert stats.bytes_sent == 1024000
        assert stats.bytes_received == 486400
        assert stats.packet_loss == 50
        # 50 loss out of 1050 total
        assert abs(stats.packet_loss_percent - (50 / 1050 * 100)) < 0.01

    def test_high_loss_scenario(self):
        """Test high packet loss scenario."""
        stats = NetStatistics()

        stats.increment_packets_sent()
        stats.increment_packets_sent()
        stats.increment_packets_sent()
        stats.increment_packet_loss()
        stats.increment_packet_loss()

        # 2 loss out of 5 total = 40%
        assert stats.packet_loss_percent == 40.0

    def test_no_traffic(self):
        """Test statistics with no traffic."""
        stats = NetStatistics()
        assert stats.packets_sent == 0
        assert stats.packets_received == 0
        assert stats.bytes_sent == 0
        assert stats.bytes_received == 0
        assert stats.packet_loss == 0
        assert stats.packet_loss_percent == 0.0
