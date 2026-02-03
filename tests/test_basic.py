"""
Basic functionality tests for LiteNetLib Python v0.9.5.2
LiteNetLib Python v0.9.5.2 基本功能测试
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from litenetlib import NetPacket, PacketProperty, NetConstants, DeliveryMethod
from litenetlib.utils.data_writer import NetDataWriter
from litenetlib.utils.data_reader import NetDataReader
from litenetlib.utils.fast_bit_converter import FastBitConverter


def test_packet_creation():
    """Test basic packet creation."""
    print("\n=== Packet Creation Test ===")

    # Create a simple CHANNELED packet
    packet = NetPacket(PacketProperty.CHANNELED, 100)
    packet.sequence = 12345
    packet.channel_id = 5

    assert packet.packet_property == PacketProperty.CHANNELED, "Property mismatch"
    assert packet.sequence == 12345, "Sequence mismatch"
    assert packet.channel_id == 5, "ChannelId mismatch"

    print(f"[OK] Packet created successfully")
    print(f"  - Property: {packet.packet_property}")
    print(f"  - Sequence: {packet.sequence}")
    print(f"  - ChannelId: {packet.channel_id}")
    print(f"  - Size: {packet.size}")

    return True


def test_data_writer_reader():
    """Test DataWriter and DataReader."""
    print("\n=== DataWriter/DataReader Test ===")

    writer = NetDataWriter()
    writer.put_string("Hello")
    writer.put_int(42)
    writer.put_short(1000)
    writer.put_byte(255)
    writer.put_bool(True)

    data = writer.to_bytes()
    reader = NetDataReader(data)

    text = reader.get_string()
    num = reader.get_int()
    short_val = reader.get_short()
    byte_val = reader.get_byte()
    bool_val = reader.get_bool()

    assert text == "Hello", f"String mismatch: {text}"
    assert num == 42, f"Int mismatch: {num}"
    assert short_val == 1000, f"Short mismatch: {short_val}"
    assert byte_val == 255, f"Byte mismatch: {byte_val}"
    assert bool_val == True, f"Bool mismatch: {bool_val}"

    print(f"[OK] DataWriter/DataReader working correctly")
    print(f"  - String: {text}")
    print(f"  - Int: {num}")
    print(f"  - Short: {short_val}")
    print(f"  - Byte: {byte_val}")
    print(f"  - Bool: {bool_val}")

    return True


def test_packet_properties():
    """Test PacketProperty enum values."""
    print("\n=== PacketProperty Enum Test ===")

    # Critical values for v0.9.5.2
    assert int(PacketProperty.ACK) == 2, f"ACK should be 2, got {int(PacketProperty.ACK)}"
    assert int(PacketProperty.EMPTY) == 17, f"EMPTY should be 17, got {int(PacketProperty.EMPTY)}"
    assert int(PacketProperty.MERGED) == 12, f"MERGED should be 12, got {int(PacketProperty.MERGED)}"

    print(f"[OK] PacketProperty enum values correct")
    print(f"  - ACK: {int(PacketProperty.ACK)}")
    print(f"  - PING: {int(PacketProperty.PING)}")
    print(f"  - PONG: {int(PacketProperty.PONG)}")
    print(f"  - MERGED: {int(PacketProperty.MERGED)}")
    print(f"  - EMPTY: {int(PacketProperty.EMPTY)}")

    return True


def test_constants():
    """Test NetConstants."""
    print("\n=== NetConstants Test ===")

    # Critical constants for v0.9.5.2
    assert NetConstants.PROTOCOL_ID == 11, f"PROTOCOL_ID should be 11, got {NetConstants.PROTOCOL_ID}"
    assert NetConstants.HEADER_SIZE == 1, f"HEADER_SIZE should be 1, got {NetConstants.HEADER_SIZE}"
    assert NetConstants.CHANNELED_HEADER_SIZE == 4, f"CHANNELED_HEADER_SIZE should be 4, got {NetConstants.CHANNELED_HEADER_SIZE}"

    print(f"[OK] NetConstants correct")
    print(f"  - PROTOCOL_ID: {NetConstants.PROTOCOL_ID}")
    print(f"  - HEADER_SIZE: {NetConstants.HEADER_SIZE}")
    print(f"  - CHANNELED_HEADER_SIZE: {NetConstants.CHANNELED_HEADER_SIZE}")
    print(f"  - MAX_SEQUENCE: {NetConstants.MAX_SEQUENCE}")
    print(f"  - MTU options: {len(NetConstants.POSSIBLE_MTU)}")

    return True


def test_fast_bit_converter():
    """Test FastBitConverter."""
    print("\n=== FastBitConverter Test ===")

    # Test little-endian conversion
    buffer = bytearray(4)
    value = 0x12345678
    FastBitConverter.get_bytes(buffer, 0, value)

    # Little-endian: 0x78 0x56 0x34 0x12
    assert buffer[0] == 0x78, f"First byte should be 0x78, got {buffer[0]}"
    assert buffer[1] == 0x56, f"Second byte should be 0x56, got {buffer[1]}"
    assert buffer[2] == 0x34, f"Third byte should be 0x34, got {buffer[2]}"
    assert buffer[3] == 0x12, f"Fourth byte should be 0x12, got {buffer[3]}"

    print(f"[OK] FastBitConverter working correctly")
    print(f"  - Value: 0x{value:08X}")
    print(f"  - Bytes: {[f'0x{b:02X}' for b in buffer]}")

    return True


def run_all_tests():
    """Run all basic tests."""
    print("=" * 70)
    print("LiteNetLib Python v0.9.5.2 - Basic Functionality Tests")
    print("=" * 70)

    tests = [
        ("Packet Creation", test_packet_creation),
        ("DataWriter/DataReader", test_data_writer_reader),
        ("PacketProperty Enum", test_packet_properties),
        ("NetConstants", test_constants),
        ("FastBitConverter", test_fast_bit_converter),
    ]

    passed = 0
    failed = 0

    for name, test_func in tests:
        try:
            if test_func():
                passed += 1
        except Exception as e:
            print(f"\n[FAILED] {name}: {e}")
            failed += 1
            import traceback
            traceback.print_exc()

    print("\n" + "=" * 70)
    print(f"Test Results: {passed} passed, {failed} failed")
    print("=" * 70)

    return failed == 0


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
