"""
Basic import and functionality test for LiteNetLib Python

This test verifies that all basic components can be imported and instantiated.
"""


def test_imports():
    """Test all basic imports"""
    print("Testing imports...")

    # Core imports
    from litenetlib import DeliveryMethod, NetConstants, NetDebug, NetUtils
    print("[OK] Core imports successful")

    # Packet imports
    from litenetlib.packets import NetPacket, NetPacketPool, PacketProperty
    print("[OK] Packet imports successful")

    # Utils imports
    from litenetlib.utils import (
        NetDataReader,
        NetDataWriter,
        FastBitConverter,
        CRC32C,
        INetSerializable,
    )
    print("[OK] Utils imports successful")

    # Socket imports
    from litenetlib import NetSocket, NetStatistics
    print("[OK] Socket imports successful")

    # Event imports
    from litenetlib import INetEventListener, EventBasedNetListener, ConnectionRequest
    print("[OK] Event imports successful")

    # Channel imports
    from litenetlib.channels import BaseChannel, ReliableChannel, SequencedChannel
    print("[OK] Channel imports successful")

    # Layer imports
    from litenetlib.layers import PacketLayerBase, Crc32cLayer, XorEncryptLayer
    print("[OK] Layer imports successful")

    print("\nAll imports successful!\n")


def test_constants():
    """Test constants and enums"""
    from litenetlib import DeliveryMethod, NetConstants

    print("Testing constants...")

    # Test DeliveryMethod enum
    assert DeliveryMethod.Unreliable == 4
    assert DeliveryMethod.ReliableUnordered == 0
    assert DeliveryMethod.Sequenced == 1
    assert DeliveryMethod.ReliableOrdered == 2
    assert DeliveryMethod.ReliableSequenced == 3
    print("[OK] DeliveryMethod enum values correct")

    # Test NetConstants
    assert NetConstants.MaxPacketSize > 0
    assert NetConstants.HeaderSize == 1
    assert NetConstants.MaxSequence == 32768
    print("[OK] NetConstants values correct")

    print("[OK] Constants tests passed!\n")


def test_data_writer_reader():
    """Test data serialization"""
    from litenetlib.utils import NetDataWriter, NetDataReader

    print("Testing data serialization...")

    # Create writer
    writer = NetDataWriter()
    writer.put_int(42)
    writer.put_float(3.14)
    writer.put_string("Hello, LiteNetLib!")
    writer.put_bool(True)

    # Create reader from writer data
    reader = NetDataReader(writer.data)

    assert reader.get_int() == 42
    assert abs(reader.get_float() - 3.14) < 0.001
    assert reader.get_string() == "Hello, LiteNetLib!"
    assert reader.get_bool() is True

    print("[OK] Data serialization round-trip successful")
    print("[OK] Data serialization tests passed!\n")


def test_packets():
    """Test packet creation and properties"""
    from litenetlib.packets import NetPacket, NetPacketPool, PacketProperty
    from litenetlib.constants import NetConstants

    print("Testing packets...")

    # Test packet pool
    pool = NetPacketPool()
    packet = pool.get_packet(100, None)

    assert packet is not None
    assert packet.size == 100

    # Recycle packet
    pool.recycle(packet)
    assert pool._count == 1

    # Get packet with property
    packet2 = pool.get_packet(50, PacketProperty.Channeled)
    assert packet2.packet_property == PacketProperty.Channeled

    # Test packet properties
    packet3 = NetPacket(100, PacketProperty.Ping)
    packet3.connection_number = 2
    packet3.sequence = 12345

    assert packet3.packet_property == PacketProperty.Ping
    assert packet3.connection_number == 2
    assert packet3.sequence == 12345
    assert not packet3.is_fragmented

    packet3.mark_fragmented()
    assert packet3.is_fragmented

    print("[OK] Packet creation and properties work")
    print("[OK] Packet tests passed!\n")


def test_crc32c():
    """Test CRC32C checksum"""
    from litenetlib.utils import CRC32C

    print("Testing CRC32C...")

    # Test with known vectors (if available)
    test_data = b"Hello, LiteNetLib!"
    checksum = CRC32C.compute(test_data)

    assert checksum is not None
    assert isinstance(checksum, int)
    assert 0 <= checksum <= 0xFFFFFFFF

    print(f"[OK] CRC32C computed: 0x{checksum:08X}")
    print("[OK] CRC32C tests passed!\n")


def test_net_utils():
    """Test network utilities"""
    from litenetlib.net_utils import NetUtils, LocalAddrType

    print("Testing network utilities...")

    # Test address resolution
    addr = NetUtils.resolve_address("localhost")
    assert addr == "127.0.0.1" or addr == "::1"
    print(f"[OK] Localhost resolved to: {addr}")

    # Test local IP detection
    local_ips = NetUtils.get_local_ip_list(LocalAddrType.IPv4)
    assert len(local_ips) > 0
    print(f"[OK] Found {len(local_ips)} local IPv4 addresses")

    # Test sequence number math
    result = NetUtils.relative_sequence_number(10, 5)
    print(f"[OK] Relative sequence: {result}")

    print("[OK] Network utilities tests passed!\n")


def test_layers():
    """Test packet processing layers"""
    from litenetlib.layers import Crc32cLayer, XorEncryptLayer

    print("Testing packet layers...")

    # Test CRC32C layer
    crc_layer = Crc32cLayer()
    data = bytearray(b"Test data....")  # Extra space for 4-byte checksum
    crc_layer.process_out_bound_packet(data, 0, 9)  # Only process 9 bytes of data
    print(f"[OK] CRC32C layer processed data: {len(data)} bytes")

    # Test XOR layer
    xor_layer = XorEncryptLayer(b"secret_key")
    data2 = bytearray(b"Test data")
    xor_layer.process_out_bound_packet(data2, 0, 9)  # Encrypt
    result = xor_layer.process_in_bound_packet(data2, 0, 9)  # Decrypt back
    assert result is True
    assert bytes(data2) == b"Test data"  # Should be decrypted back
    print("[OK] XOR encryption/decryption works")

    print("[OK] Packet layer tests passed!\n")


def main():
    """Run all tests"""
    print("=" * 60)
    print("LiteNetLib Python - Basic Functionality Test")
    print("=" * 60)
    print()

    try:
        test_imports()
        test_constants()
        test_data_writer_reader()
        test_packets()
        test_crc32c()
        test_net_utils()
        test_layers()

        print("=" * 60)
        print("ALL TESTS PASSED!")
        print("=" * 60)
        return 0
    except Exception as e:
        print(f"\nTEST FAILED: {e}")
        import traceback

        traceback.print_exc()
        return 1


if __name__ == "__main__":
    import sys

    sys.exit(main())
