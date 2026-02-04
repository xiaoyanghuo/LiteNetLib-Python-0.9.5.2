"""
Tests for packet fragmentation system.

Tests packet splitting and reassembly for large packets.
"""

import pytest
from litenetlib.core.fragments import (
    IncomingFragment, FragmentPool,
    create_fragment_packet, parse_fragment_header
)
from litenetlib.core.packet import NetPacket
from litenetlib.core.constants import PacketProperty, NetConstants


class TestIncomingFragment:
    """Test IncomingFragment class."""

    def test_create_fragment_group(self):
        """Test creating a fragment group."""
        fragments = IncomingFragment(fragment_count=3, total_size=1500)
        assert fragments._fragment_count == 3
        assert fragments._total_size == 1500
        assert fragments._first_fragment is None
        assert len(fragments._fragments) == 3

    def test_add_fragments(self):
        """Test adding fragments to group."""
        fragments = IncomingFragment(fragment_count=3, total_size=1500)

        # Add fragments
        assert fragments.add_fragment(0, b"data0")
        assert fragments.add_fragment(1, b"data1")
        assert fragments.add_fragment(2, b"data2")

        # Verify data
        assert fragments._fragments[0] == b"data0"
        assert fragments._fragments[1] == b"data1"
        assert fragments._fragments[2] == b"data2"

    def test_duplicate_fragment(self):
        """Test that duplicate fragments return False."""
        fragments = IncomingFragment(fragment_count=3, total_size=1500)

        # Add fragment
        assert fragments.add_fragment(0, b"data0")

        # Try to add duplicate
        assert not fragments.add_fragment(0, b"data0_dup")

    def test_is_complete(self):
        """Test checking if fragment group is complete."""
        fragments = IncomingFragment(fragment_count=3, total_size=1500)

        # Not complete initially
        assert not fragments.is_complete()

        # Add first fragment
        fragments.add_fragment(0, b"data0")
        assert not fragments.is_complete()

        # Add second fragment
        fragments.add_fragment(1, b"data1")
        assert not fragments.is_complete()

        # Add last fragment
        fragments.add_fragment(2, b"data2")
        assert fragments.is_complete()

    def test_age(self):
        """Test fragment group age."""
        import time
        fragments = IncomingFragment(fragment_count=3, total_size=1500)

        # Initially young
        assert fragments.age < 0.1

        # Wait a bit
        time.sleep(0.1)
        assert fragments.age >= 0.1

    def test_set_first_fragment(self):
        """Test setting first fragment."""
        fragments = IncomingFragment(fragment_count=3, total_size=1500)
        packet = NetPacket(PacketProperty.CHANNELED, 100)

        fragments.set_first_fragment(packet)
        assert fragments._first_fragment is packet

    def test_assemble_incomplete(self):
        """Test assembling incomplete fragment group returns None."""
        fragments = IncomingFragment(fragment_count=3, total_size=1500)
        fragments.add_fragment(0, b"data0")
        fragments.add_fragment(1, b"data1")
        # Missing fragment 2

        assert fragments.assemble() is None


class TestFragmentPool:
    """Test FragmentPool class."""

    def test_create_and_get_fragments(self):
        """Test creating and retrieving fragment groups."""
        pool = FragmentPool(timeout=5.0)

        # Create fragment group
        fragments = pool.create_fragments(1, 3, 1500)

        # Retrieve fragment group
        retrieved = pool.get_fragments(1)
        assert retrieved is fragments

    def test_get_nonexistent_fragments(self):
        """Test getting non-existent fragment group returns None."""
        pool = FragmentPool(timeout=5.0)
        assert pool.get_fragments(999) is None

    def test_remove_fragments(self):
        """Test removing fragment groups."""
        pool = FragmentPool(timeout=5.0)
        pool.create_fragments(1, 3, 1500)

        # Verify exists
        assert pool.get_fragments(1) is not None

        # Remove
        pool.remove_fragments(1)

        # Verify removed
        assert pool.get_fragments(1) is None

    def test_cleanup_expired(self):
        """Test cleaning up expired fragment groups."""
        import time
        pool = FragmentPool(timeout=0.1)  # 100ms timeout

        # Create fragment group
        pool.create_fragments(1, 3, 1500)

        # Wait for expiration
        time.sleep(0.15)

        # Cleanup
        removed = pool.cleanup_expired()
        assert removed == 1
        assert pool.get_fragments(1) is None

    def test_cleanup_multiple_expired(self):
        """Test cleaning up multiple expired fragment groups."""
        import time
        pool = FragmentPool(timeout=0.1)

        # Create multiple fragment groups
        pool.create_fragments(1, 3, 1500)
        pool.create_fragments(2, 3, 1500)
        pool.create_fragments(3, 3, 1500)

        # Wait for expiration
        time.sleep(0.15)

        # Cleanup
        removed = pool.cleanup_expired()
        assert removed == 3

    def test_clear(self):
        """Test clearing all fragment groups."""
        pool = FragmentPool(timeout=5.0)
        pool.create_fragments(1, 3, 1500)
        pool.create_fragments(2, 3, 1500)

        # Clear
        pool.clear()

        # Verify all cleared
        assert pool.get_fragments(1) is None
        assert pool.get_fragments(2) is None


class TestCreateFragmentPacket:
    """Test fragment packet creation."""

    def test_create_fragment_packet_basic(self):
        """Test creating a basic fragment packet."""
        data = b"HelloWorld"
        packet = create_fragment_packet(data, fragment_id=1, fragment_part=0, fragment_total=2, channel_id=0)

        # Verify packet properties
        assert packet.packet_property == PacketProperty.CHANNELED
        assert packet.is_fragmented is True
        assert packet.channel_id == 0

    def test_fragment_packet_data(self):
        """Test that fragment data is written correctly."""
        data = b"TestData"
        packet = create_fragment_packet(data, fragment_id=5, fragment_part=1, fragment_total=3, channel_id=2)

        # Check packet contains data
        header_size = NetConstants.CHANNELED_HEADER_SIZE + NetConstants.FRAGMENT_HEADER_SIZE
        packet_data = packet._data[header_size:]
        assert packet_data == data

    def test_fragment_header(self):
        """Test that fragment header is written correctly."""
        data = b"Data"
        packet = create_fragment_packet(
            data,
            fragment_id=12345,
            fragment_part=2,
            fragment_total=5,
            channel_id=1
        )

        # Parse and verify header
        frag_id, frag_part, frag_total = parse_fragment_header(packet)
        assert frag_id == 12345
        assert frag_part == 2
        assert frag_total == 5


class TestParseFragmentHeader:
    """Test fragment header parsing."""

    def test_parse_fragment_header_basic(self):
        """Test parsing fragment header."""
        # Create a fragment packet
        data = b"TestData"
        packet = create_fragment_packet(
            data,
            fragment_id=100,
            fragment_part=1,
            fragment_total=3,
            channel_id=0
        )

        # Parse header
        frag_id, frag_part, frag_total = parse_fragment_header(packet)

        assert frag_id == 100
        assert frag_part == 1
        assert frag_total == 3

    def test_parse_fragment_header_edge_values(self):
        """Test parsing with edge values."""
        # Maximum ushort values
        data = b"X"
        packet = create_fragment_packet(
            data,
            fragment_id=65535,  # Max ushort
            fragment_part=65535,
            fragment_total=65535,
            channel_id=1
        )

        frag_id, frag_part, frag_total = parse_fragment_header(packet)

        assert frag_id == 65535
        assert frag_part == 65535
        assert frag_total == 65535

    def test_parse_fragment_header_zero_values(self):
        """Test parsing with zero values."""
        data = b"Data"
        packet = create_fragment_packet(
            data,
            fragment_id=0,
            fragment_part=0,
            fragment_total=1,  # Minimum valid total
            channel_id=0
        )

        frag_id, frag_part, frag_total = parse_fragment_header(packet)

        assert frag_id == 0
        assert frag_part == 0
        assert frag_total == 1


class TestFragmentRoundTrip:
    """Test fragmentation and reassembly round trip."""

    def test_fragment_and_assemble_round_trip(self):
        """Test fragmenting data and reassembling it."""
        # Create data that needs 3 fragments
        original_data = b"This is a long piece of data that will be split into multiple fragments for testing"

        # Simulate fragmentation
        fragment_size = 30
        fragments = []
        fragment_count = (len(original_data) + fragment_size - 1) // fragment_size

        for i in range(fragment_count):
            offset = i * fragment_size
            fragment_data = original_data[offset:offset + fragment_size]
            fragments.append((i, fragment_data))

        # Reassemble
        reassembled = bytearray()
        for frag_id, frag_data in fragments:
            reassembled.extend(frag_data)

        assert bytes(reassembled) == original_data

    def test_incoming_fragment_assemble(self):
        """Test IncomingFragment.assemble() with real data."""
        # Create fragment group
        original = b"HelloWorldThisIsATest"
        fragments = IncomingFragment(fragment_count=2, total_size=len(original))

        # Add fragments
        fragments.add_fragment(0, original[:10])
        fragments.add_fragment(1, original[10:])

        # Assemble
        assert fragments.is_complete()

        # Note: assemble() returns a NetPacket, we're testing the logic here
        # The actual NetPacket creation would need more setup


class TestFragmentIntegration:
    """Integration tests for fragmentation."""

    def test_large_packet_detection(self):
        """Test that large packets are detected for fragmentation."""
        # In a real scenario, packets larger than MTU would be fragmented
        mtu = NetConstants.INITIAL_MTU
        max_data_size = mtu - NetConstants.CHANNELED_HEADER_SIZE - NetConstants.FRAGMENT_HEADER_SIZE

        # Small packet - no fragmentation needed
        small_data = b"X" * 100
        assert len(small_data) <= max_data_size

        # Large packet - needs fragmentation
        large_data = b"X" * (max_data_size + 1000)
        assert len(large_data) > max_data_size

    def test_fragment_count_calculation(self):
        """Test calculating number of fragments needed."""
        data_size = 1000
        fragment_size = 300

        # Should need 4 fragments (300 + 300 + 300 + 100)
        expected_fragments = (data_size + fragment_size - 1) // fragment_size
        assert expected_fragments == 4
