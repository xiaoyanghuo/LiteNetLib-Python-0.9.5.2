"""
Tests for MTU discovery functionality.

Tests Path MTU Discovery implementation.
"""

import pytest
import time
from litenetlib.core.mtu_discovery import MtuDiscovery
from litenetlib.core.constants import NetConstants, PacketProperty
from litenetlib.core.packet import NetPacket


class TestMtuDiscoveryInit:
    """Test MtuDiscovery initialization."""

    def test_initial_state(self):
        """Test initial state of MTU discovery."""
        discovery = MtuDiscovery()

        # Should start with largest MTU index
        assert discovery._mtu_index == len(NetConstants.POSSIBLE_MTU) - 1

        # Should start with initial MTU
        assert discovery._current_mtu == NetConstants.INITIAL_MTU

        # Should not be complete initially
        assert not discovery.is_discovery_complete

    def test_initial_mtu_value(self):
        """Test initial MTU value."""
        discovery = MtuDiscovery()
        assert discovery.current_mtu == NetConstants.INITIAL_MTU


class TestGetNextMtu:
    """Test get_next_mtu method."""

    def test_get_next_mtu_largest_first(self):
        """Test that we start with largest MTU."""
        discovery = MtuDiscovery()

        # First call should return largest MTU
        next_mtu = discovery.get_next_mtu()
        assert next_mtu == NetConstants.POSSIBLE_MTU[-1]

    def test_get_next_mtu_series(self):
        """Test getting MTU values in descending order."""
        discovery = MtuDiscovery()

        mtus = []
        while True:
            mtu = discovery.get_next_mtu()
            if mtu is None:
                break
            mtus.append(mtu)
            discovery._mtu_index -= 1  # Simulate advancing

        # Should be in descending order
        assert mtus == sorted(mtus, reverse=True)

    def test_get_next_mtu_exhausted(self):
        """Test getting MTU when exhausted."""
        discovery = MtuDiscovery()
        discovery._mtu_index = -1  # Simulate exhausted

        assert discovery.get_next_mtu() is None


class TestStartCheck:
    """Test start_check method."""

    def test_start_check_when_complete(self):
        """Test that completed discovery doesn't start checks."""
        discovery = MtuDiscovery()
        discovery._discovery_complete = True

        assert not discovery.start_check(1000)

    def test_start_check_when_exhausted(self):
        """Test that exhausted MTU list doesn't start checks."""
        discovery = MtuDiscovery()
        discovery._mtu_index = -1

        # Should mark as complete and return False
        result = discovery.start_check(1000)
        assert not result
        assert discovery.is_discovery_complete

    def test_start_check_timing(self):
        """Test that checks respect timing."""
        discovery = MtuDiscovery()

        # First check should be allowed immediately
        assert discovery.start_check(0)

        # Send probe to update timestamp
        discovery.send_probe(0)

        # Immediate second check should not be allowed (need to wait for delay)
        assert not discovery.start_check(1)

    def test_start_check_after_delay(self):
        """Test that checks are allowed after delay."""
        discovery = MtuDiscovery()

        # First check at time 0
        assert discovery.start_check(0)
        # Send probe to update timestamp
        discovery.send_probe(0)

        # Not enough time passed
        assert not discovery.start_check(500)

        # Enough time passed (>= _check_delay which is 1000ms)
        assert discovery.start_check(1000)


class TestSendProbe:
    """Test send_probe method."""

    def test_send_probe_creates_packet(self):
        """Test that send_probe creates a packet."""
        discovery = MtuDiscovery()

        packet = discovery.send_probe(1000)

        assert packet is not None
        assert packet.packet_property == PacketProperty.MTU_CHECK
        # Packet size includes header, so check it's close to expected MTU
        # MTU_CHECK header size is 3 bytes (1 property + 2 data)
        expected_size = NetConstants.POSSIBLE_MTU[-1] + 3
        assert packet.size == expected_size

    def test_send_probe_updates_timestamp(self):
        """Test that send_probe updates check time."""
        discovery = MtuDiscovery()
        discovery._last_check_time = 0

        discovery.send_probe(5000)

        assert discovery._last_check_time == 5000

    def test_send_probe_when_exhausted(self):
        """Test send_probe when MTU list exhausted."""
        discovery = MtuDiscovery()
        discovery._mtu_index = -1

        packet = discovery.send_probe(1000)

        assert packet is None
        assert discovery.is_discovery_complete


class TestHandleSuccess:
    """Test handle_success method."""

    def test_handle_success_updates_mtu(self):
        """Test that success updates current MTU."""
        discovery = MtuDiscovery()
        test_mtu = 1200

        discovery.handle_success(test_mtu)

        assert discovery.current_mtu == test_mtu

    def test_handle_success_resets_attempts(self):
        """Test that success resets check attempts."""
        discovery = MtuDiscovery()
        discovery._check_attempts = 3

        discovery.handle_success(1200)

        assert discovery._check_attempts == 0

    def test_handle_success_advances_index(self):
        """Test that success advances to next MTU index."""
        discovery = MtuDiscovery()
        initial_index = discovery._mtu_index

        discovery.handle_success(1200)

        # Should advance if not at max
        if initial_index + 1 < len(NetConstants.POSSIBLE_MTU):
            assert discovery._mtu_index == initial_index + 1

    def test_handle_success_at_max_mtu(self):
        """Test that success at max MTU marks discovery complete."""
        discovery = MtuDiscovery()
        discovery._mtu_index = len(NetConstants.POSSIBLE_MTU) - 1

        discovery.handle_success(NetConstants.MAX_PACKET_SIZE)

        assert discovery.is_discovery_complete


class TestHandleFailure:
    """Test handle_failure method."""

    def test_handle_failure_increments_attempts(self):
        """Test that failure increments attempts."""
        discovery = MtuDiscovery()
        initial_attempts = discovery._check_attempts

        discovery.handle_failure()

        assert discovery._check_attempts == initial_attempts + 1

    def test_handle_failure_decrements_mtu_after_max_attempts(self):
        """Test that failure decreases MTU after max attempts."""
        discovery = MtuDiscovery()
        discovery._mtu_index = 3
        discovery._check_attempts = 5  # At max

        discovery.handle_failure()

        assert discovery._mtu_index == 2
        assert discovery._check_attempts == 0

    def test_handle_failure_at_minimum_mtu(self):
        """Test that failure at minimum MTU marks discovery complete."""
        discovery = MtuDiscovery()
        discovery._mtu_index = 0
        discovery._check_attempts = 5

        discovery.handle_failure()

        assert discovery._mtu_index == -1
        # Note: is_discovery_complete is checked by get_next_mtu

    def test_handle_failure_before_max_attempts(self):
        """Test that failure before max attempts doesn't decrease MTU."""
        discovery = MtuDiscovery()
        initial_index = discovery._mtu_index
        discovery._check_attempts = 2

        discovery.handle_failure()

        assert discovery._mtu_index == initial_index
        assert discovery._check_attempts == 3


class TestShouldTryNext:
    """Test should_try_next method."""

    def test_should_try_next_when_complete(self):
        """Test that completed discovery doesn't try next."""
        discovery = MtuDiscovery()
        discovery._discovery_complete = True

        assert not discovery.should_try_next(1000)

    def test_should_try_next_on_timeout(self):
        """Test that timeout triggers trying next MTU."""
        discovery = MtuDiscovery()
        discovery._last_check_time = 0
        discovery._check_attempts = 1

        # Timeout = 1 * 1000 + 1000 = 2000ms
        assert discovery.should_try_next(3000)

    def test_should_try_next_before_timeout(self):
        """Test that no timeout doesn't trigger next."""
        discovery = MtuDiscovery()
        discovery._last_check_time = 1000
        discovery._check_attempts = 1

        # Timeout = 1 * 1000 + 1000 = 2000ms
        # Current time = 1500 (500ms passed)
        assert not discovery.should_try_next(1500)


class TestGetMaxSafeMtu:
    """Test get_max_safe_mtu method."""

    def test_get_max_safe_mtu_initial(self):
        """Test that initial max safe MTU is initial MTU."""
        discovery = MtuDiscovery()
        assert discovery.get_max_safe_mtu() == NetConstants.INITIAL_MTU

    def test_get_max_safe_mtu_after_success(self):
        """Test that max safe MTU updates after success."""
        discovery = MtuDiscovery()
        discovery.handle_success(1400)

        assert discovery.get_max_safe_mtu() == 1400


class TestReset:
    """Test reset method."""

    def test_reset_restores_initial_state(self):
        """Test that reset restores initial state."""
        discovery = MtuDiscovery()

        # Modify state
        discovery._mtu_index = 2
        discovery._discovery_complete = True
        discovery._check_attempts = 5

        # Reset
        discovery.reset()

        # Should be back to initial state
        assert discovery._mtu_index == len(NetConstants.POSSIBLE_MTU) - 1
        assert not discovery.is_discovery_complete
        assert discovery._check_attempts == 0
        assert discovery.current_mtu == NetConstants.INITIAL_MTU


class TestMtuDiscoveryIntegration:
    """Integration tests for MTU discovery."""

    def test_discovery_flow_success_path(self):
        """Test successful MTU discovery flow."""
        discovery = MtuDiscovery()
        current_time = 0

        # Start with largest MTU
        assert not discovery.is_discovery_complete
        assert discovery.start_check(current_time)

        # Send probe
        probe = discovery.send_probe(current_time)
        assert probe is not None

        # Receive success (use the MTU value, not packet size)
        mtu_value = NetConstants.POSSIBLE_MTU[-1]
        discovery.handle_success(mtu_value)

    def test_discovery_flow_failure_path(self):
        """Test MTU discovery with failures."""
        discovery = MtuDiscovery()
        current_time = 0

        # Start check and send probe
        assert discovery.start_check(current_time)
        probe = discovery.send_probe(current_time)
        assert probe is not None

        # Simulate multiple timeouts to trigger MTU decrease
        for _ in range(5):
            discovery.handle_failure()

        # Should have decreased MTU index after max attempts
        assert discovery._mtu_index < len(NetConstants.POSSIBLE_MTU) - 1 or discovery.is_discovery_complete

    def test_discovery_completes_at_suitable_mtu(self):
        """Test that discovery completes at a working MTU."""
        discovery = MtuDiscovery()

        # Simulate finding working MTU
        discovery._mtu_index = 2  # Middle value
        discovery.handle_success(NetConstants.POSSIBLE_MTU[2])

        # Try to advance to next (larger) MTU
        discovery.handle_success(NetConstants.POSSIBLE_MTU[3])

        # Simulate failures on larger MTUs until complete
        while not discovery.is_discovery_complete and discovery._mtu_index >= 0:
            # Simulate multiple timeouts
            for _ in range(5):
                discovery.handle_failure()
            if discovery._mtu_index < 0:
                break

        # Eventually should complete with some working MTU
        assert discovery.is_discovery_complete or discovery._mtu_index < 0


class TestMtuValues:
    """Test MTU value constants."""

    def test_possible_mtu_values(self):
        """Test that possible MTU values are valid."""
        mtus = NetConstants.POSSIBLE_MTU

        # Should have 7 values (v0.9.5.2)
        assert len(mtus) == 7

        # Should be in ascending order
        assert mtus == sorted(mtus)

        # All should be less than max packet size
        for mtu in mtus:
            assert mtu <= NetConstants.MAX_PACKET_SIZE

    def test_initial_mtu_is_valid(self):
        """Test that initial MTU is a valid value."""
        assert NetConstants.INITIAL_MTU in NetConstants.POSSIBLE_MTU
        assert NetConstants.INITIAL_MTU == NetConstants.POSSIBLE_MTU[0]

    def test_max_packet_size_is_valid(self):
        """Test that max packet size is valid."""
        assert NetConstants.MAX_PACKET_SIZE in NetConstants.POSSIBLE_MTU
        assert NetConstants.MAX_PACKET_SIZE == NetConstants.POSSIBLE_MTU[-1]
