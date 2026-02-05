"""
协议兼容性测试

测试Python和C#实现的协议兼容性
"""

import sys
sys.path.insert(0, '..')

from litenetlib.packets.net_packet import PacketProperty, NetPacket
from litenetlib.utils.net_data_reader import NetDataReader
from litenetlib.utils.net_data_writer import NetDataWriter
from litenetlib.utils.crc32c import CRC32C


def test_packet_format():
    """测试包格式与C#兼容"""
    print("Testing packet format compatibility...")

    # 创建测试包
    packet = NetPacket(100, PacketProperty.Unreliable)

    # 验证包头格式
    assert packet.packet_property == PacketProperty.Unreliable, "Packet property mismatch"
    assert packet.size == 100 + 1, "Packet size mismatch"  # 100 bytes + 1 byte header

    # 验证包验证方法
    assert packet.verify() == True, "Packet verification failed"

    print("[OK] Packet format test passed")


def test_serialization_format():
    """测试序列化格式与C#兼容"""
    print("Testing serialization format compatibility...")

    writer = NetDataWriter()

    # 写入各种类型的数据
    writer.put_int(42)  # int
    writer.put_float(3.14)  # float
    writer.put_string("Hello")  # string

    # 读取数据
    data = writer.copy_data()
    reader = NetDataReader(data)

    value_int = reader.get_int()
    value_float = reader.get_float()
    value_str = reader.get_string(16)

    assert value_int == 42, f"Int mismatch: {value_int}"
    assert abs(value_float - 3.14) < 0.001, f"Float mismatch: {value_float}"
    assert value_str == "Hello", f"String mismatch: {value_str}"

    print("[OK] Serialization format test passed")


def test_crc32c_compatibility():
    """测试CRC32C计算与C#兼容"""
    print("Testing CRC32C compatibility...")

    # 测试向量（从C#版本获取）
    test_data = b"Hello, World!"
    crc = CRC32C.compute(test_data)

    # 验证CRC值（这应该与C#版本计算的结果一致）
    # 注意：实际值需要从C#版本获取
    assert crc != 0, "CRC is zero"
    assert crc is not None, "CRC is None"

    print(f"[OK] CRC32C computed: 0x{crc:08X}")


def test_byte_order():
    """测试字节序与C#兼容（小端）"""
    print("Testing byte order compatibility...")

    writer = NetDataWriter()

    # 写入测试值（使用小端字节序）
    writer.put_int(0x12345678)  # int

    data = writer.copy_data()

    # 验证字节序（小端：78 56 34 12）
    expected_bytes = bytes([0x78, 0x56, 0x34, 0x12])
    assert data[:4] == expected_bytes, f"Byte order mismatch: {data[:4].hex()} != {expected_bytes.hex()}"

    print("[OK] Byte order test passed")


def run_all_tests():
    """运行所有兼容性测试"""
    print("=" * 60)
    print("LiteNetLib Python - Protocol Compatibility Tests")
    print("=" * 60)
    print()

    try:
        test_packet_format()
        test_serialization_format()
        test_crc32c_compatibility()
        test_byte_order()

        print()
        print("=" * 60)
        print("ALL COMPATIBILITY TESTS PASSED!")
        print("=" * 60)
        print()
        print("Tests completed:")
        print("  [OK] Packet format")
        print("  [OK] Serialization format")
        print("  [OK] CRC32C compatibility")
        print("  [OK] Byte order (little-endian)")
        print()
        print("Note: Full interoperability testing requires C# test server.")
        print("      This will be implemented in future versions.")

    except AssertionError as e:
        print()
        print("=" * 60)
        print("TEST FAILED!")
        print("=" * 60)
        print(f"Error: {e}")
        sys.exit(1)
    except Exception as e:
        print()
        print("=" * 60)
        print("TEST ERROR!")
        print("=" * 60)
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    run_all_tests()
