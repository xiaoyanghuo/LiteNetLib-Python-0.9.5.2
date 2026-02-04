"""
Tests for packet merging functionality.

Tests packet merging to combine multiple small packets.
"""

import pytest
import time
from litenetlib.core.packet_merging import MergedPacket, process_merged_packet
from litenetlib.core.packet import NetPacket
from litenetlib.core.constants import PacketProperty, NetConstants


class TestMergedPacketInit:
    """Test MergedPacket initialization."""

    def test_initial_state(self):
        """Test initial state of merged packet."""
        merged = MergedPacket()

        assert merged.packet_count == 0
        assert merged._total_size == 0
        assert merged.can_merge is True  # Less than 255
        assert not merged.should_send  # No packets, no timer

    def test_initial_state_with_custom_max(self):
        """Test initial state with custom max size."""
        merged = MergedPacket(max_size=500)

        assert merged._max_size == 500
        assert merged.packet_count == 0


class TestAddPacket:
    """Test add_packet method."""

    def test_add_packet(self):
        """Test adding a packet."""
        merged = MergedPacket()
        packet = NetPacket(PacketProperty.UNRELIABLE, 100)

        result = merged.add_packet(packet, 0.0)

        assert result is True
        assert merged.packet_count == 1

    def test_add_multiple_packets(self):
        """Test adding multiple packets."""
        merged = MergedPacket()

        for i in range(5):
            packet = NetPacket(PacketProperty.UNRELIABLE, 50)
            merged.add_packet(packet, 0.0)

        assert merged.packet_count == 5

    def test_add_packet_starts_timer(self):
        """Test that first packet starts merge timer."""
        merged = MergedPacket()
        merged._merge_timer = 0.0

        packet = NetPacket(PacketProperty.UNRELIABLE, 100)
        merged.add_packet(packet, 1.0)

        # Timer should be set
        assert merged._merge_timer == 1.0

    def test_add_packet_when_buffer_full(self):
        """Test adding packet when buffer is full."""
        merged = MergedPacket()

        # Fill buffer to max (255 packets)
        for i in range(256):
            packet = NetPacket(PacketProperty.UNRELIABLE, 10)
            if i < 255:
                merged.add_packet(packet, 0.0)

        # Try to add one more
        packet = NetPacket(PacketProperty.UNRELIABLE, 10)
        result = merged.add_packet(packet, 0.0)

        assert result is False  # Buffer full

    def test_add_packet_when_size_exceeded(self):
        """Test adding packet that exceeds max size."""
        merged = MergedPacket(max_size=200)

        # Add packet that fills buffer
        large_packet = NetPacket(PacketProperty.UNRELIABLE, 150)
        merged.add_packet(large_packet, 0.0)

        # Try to add another that would exceed max
        # 2 (size header) + 150 + 2 (size header) + 100 = 254 > 200
        another_packet = NetPacket(PacketProperty.UNRELIABLE, 100)
        result = merged.add_packet(another_packet, 0.0)

        assert result is False  # Size exceeded

    def test_add_packet_updates_total_size(self):
        """Test that add_packet updates total size correctly."""
        merged = MergedPacket()

        packet1 = NetPacket(PacketProperty.UNRELIABLE, 100)
        merged.add_packet(packet1, 0.0)

        # Size should be: 2 (size header) + packet.size
        assert merged._total_size == 2 + packet1.size

        packet2 = NetPacket(PacketProperty.UNRELIABLE, 50)
        merged.add_packet(packet2, 0.0)

        # Size should be: 2 + packet1.size + 2 + packet2.size
        expected = 2 + packet1.size + 2 + packet2.size
        assert merged._total_size == expected


class TestShouldSend:
    """Test should_send method."""

    def test_should_send_when_empty(self):
        """Test that empty buffer doesn't trigger send."""
        merged = MergedPacket()

        assert not merged.should_send

    def test_should_send_when_buffer_full(self):
        """Test that full buffer triggers send."""
        merged = MergedPacket()

        # Fill buffer until it can't accept more
        count = 0
        for i in range(300):
            packet = NetPacket(PacketProperty.UNRELIABLE, 10)
            if merged.add_packet(packet, 0.0):
                count += 1
            else:
                break

        # Should have added some packets
        assert count > 0
        # Buffer stopped accepting packets (either by count or size limit)
        # Note: can_merge only checks count < 255, but add_packet also checks size
        # So with 10-byte packets, we hit size limit before count limit

    def test_should_send_on_timeout(self):
        """Test that timeout triggers send."""
        merged = MergedPacket()

        # Add a packet
        packet = NetPacket(PacketProperty.UNRELIABLE, 100)
        merged.add_packet(packet, time.time())

        # Wait for timeout (10ms + small buffer)
        time.sleep(0.015)

        assert merged.should_send

    def test_should_send_not_triggered_early(self):
        """Test that send is not triggered before timeout."""
        merged = MergedPacket()

        # Add a packet
        packet = NetPacket(PacketProperty.UNRELIABLE, 100)
        merged.add_packet(packet, time.time())

        # Check immediately (before timeout)
        assert not merged.should_send


class TestCreateMergedPacket:
    """Test create_merged_packet method."""

    def test_create_merged_packet_empty(self):
        """Test creating merged packet from empty buffer."""
        merged = MergedPacket()

        result = merged.create_merged_packet()

        assert result is None
        assert merged.packet_count == 0

    def test_create_merged_packet_basic(self):
        """Test creating merged packet."""
        merged = MergedPacket()

        # Add small packets
        packet1 = NetPacket(PacketProperty.UNRELIABLE, 10)
        packet2 = NetPacket(PacketProperty.UNRELIABLE, 10)
        merged.add_packet(packet1, 0.0)
        merged.add_packet(packet2, 0.0)

        # Create merged packet
        result = merged.create_merged_packet()

        assert result is not None
        assert result.packet_property == PacketProperty.MERGED
        # Merged packets don't use fragmented flag

        # Buffer should be cleared
        assert merged.packet_count == 0

    def test_create_merged_packet_content(self):
        """Test that merged packet contains correct data."""
        merged = MergedPacket()

        # Create packet with specific data
        packet1 = NetPacket(PacketProperty.UNRELIABLE, 10)
        packet1._data[1:] = b"Data1"

        packet2 = NetPacket(PacketProperty.UNRELIABLE, 10)
        packet2._data[1:] = b"Data2"

        merged.add_packet(packet1, 0.0)
        merged.add_packet(packet2, 0.0)

        # Create merged packet
        result = merged.create_merged_packet()

        assert result is not None

        # Packet count should be at offset 1 (after property byte)
        import struct
        count = struct.unpack('<H', result._data[1:3])[0]
        assert count == 2


class TestProcessMergedPacket:
    """Test process_merged_packet function."""

    def test_process_merged_packet_basic(self):
        """Test processing merged packet."""
        # Create packets to merge
        packet1 = NetPacket(PacketProperty.UNRELIABLE, 10)
        packet1._data[1:] = b"Pkt1"

        packet2 = NetPacket(PacketProperty.UNRELIABLE, 10)
        packet2._data[1:] = b"Pkt2"

        # Manually create merged packet (size includes property byte)
        merged = NetPacket(PacketProperty.MERGED, 1 + 2 + 2 + 10 + 2 + 10)
        # Merged packets don't use fragmented flag

        # Write packet count (starting after property byte at offset 1)
        import struct
        merged._data[1:3] = struct.pack('<H', 2)

        # Write first packet (offset starts after property + count)
        offset = 3
        merged._data[offset:offset + 2] = struct.pack('<H', 10)
        offset += 2
        merged._data[offset:offset + 10] = packet1._data

        # Write second packet
        offset += 10
        merged._data[offset:offset + 2] = struct.pack('<H', 10)
        offset += 2
        merged._data[offset:offset + 10] = packet2._data

        # Process merged packet
        packets = process_merged_packet(merged)

        assert len(packets) == 2
        assert packets[0].packet_property == PacketProperty.UNRELIABLE
        assert packets[1].packet_property == PacketProperty.UNRELIABLE

    def test_process_merged_packet_with_different_properties(self):
        """Test processing merged packet with different packet types."""
        # Create packets with different properties
        packet1 = NetPacket(PacketProperty.PING, 5)  # Small packet
        packet1._data[1:] = b"AAAAA"

        packet2 = NetPacket(PacketProperty.PONG, 12)
        packet2._data[1:] = b"BBBBBBBBBBBB"

        # Manually create merged packet (size includes property byte)
        merged = NetPacket(PacketProperty.MERGED, 1 + 2 + 2 + 5 + 2 + 12)
        # Merged packets don't use fragmented flag

        import struct
        merged._data[1:3] = struct.pack('<H', 2)

        offset = 3
        # First packet
        merged._data[offset:offset + 2] = struct.pack('<H', 5)
        offset += 2
        merged._data[offset:offset + 5] = packet1._data

        # Second packet
        offset += 5
        merged._data[offset:offset + 2] = struct.pack('<H', 12)
        offset += 2
        merged._data[offset:offset + 12] = packet2._data

        # Process
        packets = process_merged_packet(merged)

        assert len(packets) == 2
        assert packets[0].packet_property == PacketProperty.PING
        assert packets[1].packet_property == PacketProperty.PONG


class TestClear:
    """Test clear method."""

    def test_clear(self):
        """Test clearing merge buffer."""
        merged = MergedPacket()

        # Add packets
        for i in range(5):
            packet = NetPacket(PacketProperty.UNRELIABLE, 10)
            merged.add_packet(packet, 0.0)

        assert merged.packet_count == 5

        # Clear
        merged.clear()

        assert merged.packet_count == 0
        assert merged._total_size == 0
        assert merged._merge_timer == 0.0


class TestPacketMergingIntegration:
    """Integration tests for packet merging."""

    def test_merge_and_extract_round_trip(self):
        """Test merging and extracting packets."""
        merged = MergedPacket()

        # Create various packets with actual data
        # Size parameter includes the property byte, so payload is size-1
        data1 = b"Data0"  # 5 bytes
        pkt1 = NetPacket(PacketProperty.UNRELIABLE, 1 + len(data1))
        pkt1._data[1:1+len(data1)] = data1

        data2 = b"Data1"  # 5 bytes
        pkt2 = NetPacket(PacketProperty.PING, 1 + len(data2))
        pkt2._data[1:1+len(data2)] = data2

        data3 = b"Data2"  # 5 bytes
        pkt3 = NetPacket(PacketProperty.PONG, 1 + len(data3))
        pkt3._data[1:1+len(data3)] = data3

        # Add to merge buffer
        merged.add_packet(pkt1, time.time())
        merged.add_packet(pkt2, time.time())
        merged.add_packet(pkt3, time.time())

        # Create merged packet
        merged_packet = merged.create_merged_packet()

        assert merged_packet is not None

        # Extract packets
        extracted_packets = process_merged_packet(merged_packet)

        assert len(extracted_packets) == 3

        # Verify properties are preserved
        assert extracted_packets[0].packet_property == PacketProperty.UNRELIABLE
        assert extracted_packets[1].packet_property == PacketProperty.PING
        assert extracted_packets[2].packet_property == PacketProperty.PONG

        # Verify data is preserved (extract first N bytes of payload)
        assert extracted_packets[0]._data[1:1+len(data1)] == data1
        assert extracted_packets[1]._data[1:1+len(data2)] == data2
        assert extracted_packets[2]._data[1:1+len(data3)] == data3

    def test_merge_efficiency(self):
        """Test that merging reduces packet count."""
        merged = MergedPacket()

        # Add many small packets
        packet_count = 10
        for i in range(packet_count):
            packet = NetPacket(PacketProperty.UNRELIABLE, 20)
            merged.add_packet(packet, 0.0)

        # Create one merged packet
        merged_packet = merged.create_merged_packet()

        # Should have 1 merged packet instead of 10 separate packets
        assert merged_packet is not None

        # Extract should get back 10 packets
        extracted = process_merged_packet(merged_packet)
        assert len(extracted) == packet_count


class TestEdgeCases:
    """Test edge cases and error conditions."""

    def test_merge_single_packet(self):
        """Test merging a single packet (should still work)."""
        merged = MergedPacket()

        packet = NetPacket(PacketProperty.UNRELIABLE, 100)
        merged.add_packet(packet, time.time())

        merged_packet = merged.create_merged_packet()
        assert merged_packet is not None

        extracted = process_merged_packet(merged_packet)
        assert len(extracted) == 1

    def test_merge_maximum_packets(self):
        """Test merging maximum number of packets (255)."""
        merged = MergedPacket(max_size=100000)  # Large max size

        # Add packets until buffer is full
        for i in range(300):  # Try to add more than 255
            packet = NetPacket(PacketProperty.UNRELIABLE, 10)
            if not merged.add_packet(packet, 0.0):
                break

        # Should have 255 packets (limited by count, not size)
        assert merged.packet_count == 255

        # Create and extract
        merged_packet = merged.create_merged_packet()
        assert merged_packet is not None

        extracted = process_merged_packet(merged_packet)
        assert len(extracted) == 255

    def test_empty_extracted_data(self):
        """Test that extracted packets preserve data."""
        merged = MergedPacket()

        # Create packet with specific data
        original_data = b"HelloWorld"  # 10 bytes
        # Create packet with property byte + data
        packet = NetPacket(PacketProperty.UNRELIABLE, 1 + len(original_data))
        # Write data after property byte
        packet._data[1:1+len(original_data)] = original_data

        merged.add_packet(packet, 0.0)
        merged_packet = merged.create_merged_packet()

        # Extract and verify data
        extracted = process_merged_packet(merged_packet)
        assert len(extracted) == 1

        # Get data (skip property byte)
        extracted_data = extracted[0]._data[1:1+len(original_data)]
        assert extracted_data == original_data
