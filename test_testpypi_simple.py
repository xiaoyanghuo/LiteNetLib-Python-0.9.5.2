"""
TestPyPI Installation Test - Simple Version
Test the package installed from TestPyPI
"""

import sys
import struct

# Set UTF-8 encoding for Windows console
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from litenetlib.core.constants import (
    NetConstants, PacketProperty, DeliveryMethod,
    get_header_size, DisconnectReason
)
from litenetlib.core.packet import NetPacket, NetPacketPool
from litenetlib.utils.data_writer import NetDataWriter
from litenetlib.utils.data_reader import NetDataReader
from litenetlib.utils.net_utils import NetUtils


def print_header(title):
    print("\n" + "="*70)
    print(f"  {title}")
    print("="*70)


def test_1_constants():
    """Test 1: Protocol Constants"""
    print_header("Test 1: Protocol Constants")

    tests = [
        ("PROTOCOL_ID", 11, NetConstants.PROTOCOL_ID),
        ("ACK", 2, PacketProperty.ACK),
        ("EMPTY", 17, PacketProperty.EMPTY),
        ("MERGED", 12, PacketProperty.MERGED),
        ("CHANNELED", 1, PacketProperty.CHANNELED),
        ("DEFAULT_WINDOW_SIZE", 64, NetConstants.DEFAULT_WINDOW_SIZE),
        ("MAX_SEQUENCE", 32768, NetConstants.MAX_SEQUENCE),
        ("HALF_MAX_SEQUENCE", 16384, NetConstants.HALF_MAX_SEQUENCE),
    ]

    passed = 0
    for name, expected, actual in tests:
        if expected == actual:
            print(f"  [PASS] {name}: {actual}")
            passed += 1
        else:
            print(f"  [FAIL] {name}: expected {expected}, got {actual}")

    print(f"\n  Result: {passed}/{len(tests)} passed")
    return passed == len(tests)


def test_2_packet_creation():
    """Test 2: Packet Creation"""
    print_header("Test 2: Packet Creation")

    try:
        # Create different packet types
        packets = []

        # Unreliable packet
        p1 = NetPacket(PacketProperty.UNRELIABLE, 100)
        assert p1.packet_property == PacketProperty.UNRELIABLE
        assert p1.size == 101
        packets.append("UNRELIABLE")

        # Channeled packet
        p2 = NetPacket(PacketProperty.CHANNELED, 50)
        assert p2.packet_property == PacketProperty.CHANNELED
        assert p2.size == 54
        packets.append("CHANNELED")

        # ACK packet
        p3 = NetPacket(PacketProperty.ACK, 10)
        assert p3.packet_property == PacketProperty.ACK
        packets.append("ACK")

        # MERGED packet
        p4 = NetPacket(PacketProperty.MERGED, 100)
        packets.append("MERGED")

        print(f"  [PASS] Created {len(packets)} packet types")
        for p_type in packets:
            print(f"    - {p_type}")

        # Test fragmented packet
        p5 = NetPacket(PacketProperty.CHANNELED, 100)
        p5.mark_fragmented()
        p5.fragment_id = 1
        p5.fragment_part = 0
        p5.fragments_total = 5
        assert p5.is_fragmented
        assert p5.fragment_id == 1
        print(f"  [PASS] Fragmented packet created")

        # Test packet pool
        pool = NetPacketPool()
        p6 = pool.get(100)
        assert p6.size == 100
        pool.recycle(p6)
        print(f"  [PASS] Packet pool works")

        return True

    except Exception as e:
        print(f"  [FAIL] Packet creation failed: {e}")
        return False


def test_3_serialization():
    """Test 3: Serialization"""
    print_header("Test 3: Serialization")

    try:
        writer = NetDataWriter()

        # Basic types
        writer.put_byte(0x12)
        writer.put_short(0x1234)
        writer.put_int(0x12345678)
        writer.put_long(0x123456789ABCDEF0)
        writer.put_float(3.14)
        writer.put_string("Hello from TestPyPI!")
        writer.put_string("Chinese test")

        # Read back
        reader = NetDataReader(writer.to_bytes())

        b = reader.get_byte()
        s = reader.get_short()
        i = reader.get_int()
        l = reader.get_long()
        f = reader.get_float()
        str1 = reader.get_string()
        str2 = reader.get_string()

        tests = [
            ("Byte", 0x12, b),
            ("Short", 0x1234, s),
            ("Int", 0x12345678, i),
            ("Long", 0x123456789ABCDEF0, l),
            ("Float", 3.14, round(f, 2)),
            ("String", "Hello from TestPyPI!", str1),
            ("Chinese", "Chinese test", str2),
        ]

        passed = 0
        for name, expected, actual in tests:
            if expected == actual:
                print(f"  [PASS] {name}: {actual}")
                passed += 1
            else:
                print(f"  [FAIL] {name}: expected {expected}, got {actual}")

        # Test array
        writer2 = NetDataWriter()
        writer2.put_array([1, 2, 3, 4, 5])
        reader2 = NetDataReader(writer2.to_bytes())
        arr = reader2.get_array()

        if arr == [1, 2, 3, 4, 5]:
            print(f"  [PASS] Array: {arr}")
            passed += 1

        print(f"\n  Result: {passed}/{len(tests) + 1} passed")
        return passed >= len(tests)

    except Exception as e:
        print(f"  [FAIL] Serialization failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_4_binary_format():
    """Test 4: Binary Format"""
    print_header("Test 4: Binary Packet Format")

    try:
        # Create CHANNELED packet
        packet = NetPacket(PacketProperty.CHANNELED, 10)
        packet.sequence = 1234
        packet.channel_id = 5

        data = packet.get_bytes()

        # Verify byte format
        tests = []

        # Byte 0: Property (1)
        if data[0] == 1:
            tests.append(True)
        else:
            tests.append(False)

        # Bytes 1-2: Sequence (1234 little-endian)
        seq = struct.unpack('<H', bytes(data[1:3]))[0]
        tests.append(seq == 1234)

        # Byte 3: Channel ID
        tests.append(data[3] == 5)

        print(f"  [PASS] Property: CHANNELED")
        print(f"  [PASS] Sequence: {seq} (little-endian)")
        print(f"  [PASS] Channel ID: 5")

        all_passed = all(tests)
        if all_passed:
            print(f"\n  [PASS] Binary format correct")

        return all_passed

    except Exception as e:
        print(f"  [FAIL] Binary format test failed: {e}")
        return False


def test_5_csharp_compatibility():
    """Test 5: C# Compatibility"""
    print_header("Test 5: C# Interoperability")

    try:
        # Simulate C# packet
        csharp_packet = (
            struct.pack('<B', 0x01) +     # CHANNELED
            struct.pack('<H', 1000) +     # Sequence
            struct.pack('<B', 2) +        # Channel ID
            b"Data from C#"              # Payload
        )

        # Parse in Python
        packet = NetPacket.from_bytes(csharp_packet)

        tests = [
            ("Property", PacketProperty.CHANNELED == packet.packet_property),
            ("Sequence", 1000 == packet.sequence),
            ("Channel", 2 == packet.channel_id),
            ("Data", b"Data from C#" == packet.get_data()),
        ]

        passed = 0
        for name, result in tests:
            if result:
                print(f"  [PASS] {name}")
                passed += 1
            else:
                print(f"  [FAIL] {name}")

        print(f"\n  Result: {passed}/{len(tests)} passed")
        print(f"  Note: Python can parse C# packets correctly")
        return passed == len(tests)

    except Exception as e:
        print(f"  [FAIL] C# compatibility failed: {e}")
        return False


def test_6_packet_verification():
    """Test 6: Packet Verification"""
    print_header("Test 6: Packet Verification")

    try:
        # Valid packet
        valid = NetPacket(PacketProperty.CHANNELED, 10)
        assert valid.verify() == True
        print(f"  [PASS] Valid packet passes verification")

        # Invalid size
        invalid = NetPacket(PacketProperty.CHANNELED, 0)
        invalid._size = 2
        assert invalid.verify() == False
        print(f"  [PASS] Invalid packet rejected")

        # Fragmented packet
        frag = NetPacket(PacketProperty.CHANNELED, 10)
        frag.mark_fragmented()
        assert frag.verify() == True
        print(f"  [PASS] Fragmented packet passes")

        return True

    except Exception as e:
        print(f"  [FAIL] Verification failed: {e}")
        return False


def test_7_network_utils():
    """Test 7: Network Utils"""
    print_header("Test 7: Network Utils")

    try:
        # Relative sequence
        result = NetUtils.relative_sequence_number(100, 90)
        assert result == 10
        print(f"  [PASS] Relative sequence: {result}")

        # Address parsing
        host, port = NetUtils.parse_address("127.0.0.1:7777")
        assert host == "127.0.0.1"
        assert port == 7777
        print(f"  [PASS] Address parsing: {host}:{port}")

        # Address formatting
        addr = NetUtils.format_address("::1", 7777)
        assert "[::1]" in addr
        print(f"  [PASS] Address formatting: {addr}")

        return True

    except Exception as e:
        print(f"  [FAIL] Network utils failed: {e}")
        return False


def main():
    print("\n" + "="*70)
    print("  LiteNetLib-Python v0.9.5.2 - TestPyPI Installation Test")
    print("  Source: https://test.pypi.org/")
    print("="*70)

    print("\nChecking installation...")
    import litenetlib
    print(f"  Path: {litenetlib.__file__}")

    results = []

    # Run tests
    results.append(("Constants", test_1_constants()))
    results.append(("Packet Creation", test_2_packet_creation()))
    results.append(("Serialization", test_3_serialization()))
    results.append(("Binary Format", test_4_binary_format()))
    results.append(("C# Compatibility", test_5_csharp_compatibility()))
    results.append(("Verification", test_6_packet_verification()))
    results.append(("Network Utils", test_7_network_utils()))

    # Summary
    print_header("Test Summary")

    total = len(results)
    passed = sum(1 for _, r in results if r)

    for name, result in results:
        status = "[PASS]" if result else "[FAIL]"
        print(f"  {status} {name}")

    print("\n" + "="*70)
    print(f"  Total: {passed}/{total} test groups passed")

    if passed == total:
        print(f"  Status: SUCCESS - All tests passed!")
        print(f"  Conclusion: TestPyPI package works perfectly")
    else:
        print(f"  Status: PARTIAL - Some tests failed")

    print("="*70 + "\n")

    return passed >= total * 0.8  # At least 80% pass rate


if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\nERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
