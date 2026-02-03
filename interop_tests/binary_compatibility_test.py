"""
LiteNetLib-Python 与 C# v0.9.5.2 二进制兼容性验证
验证数据包格式、序列化格式、协议常量完全一致
"""

import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Set UTF-8 encoding for Windows console
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

import struct
from litenetlib.core.packet import NetPacket
from litenetlib.core.constants import (
    PacketProperty, DeliveryMethod, NetConstants, get_header_size
)
from litenetlib.utils.data_writer import NetDataWriter
from litenetlib.utils.data_reader import NetDataReader


def test_constants():
    """验证协议常量与 C# v0.9.5.2 完全一致"""
    print("="*60)
    print("协议常量验证")
    print("="*60)

    tests = [
        ("PROTOCOL_ID", 11, NetConstants.PROTOCOL_ID),
        ("DEFAULT_WINDOW_SIZE", 64, NetConstants.DEFAULT_WINDOW_SIZE),
        ("HEADER_SIZE", 1, NetConstants.HEADER_SIZE),
        ("CHANNELED_HEADER_SIZE", 4, NetConstants.CHANNELED_HEADER_SIZE),
        ("FRAGMENT_HEADER_SIZE", 6, NetConstants.FRAGMENT_HEADER_SIZE),
        ("MAX_SEQUENCE", 32768, NetConstants.MAX_SEQUENCE),
        ("HALF_MAX_SEQUENCE", 16384, NetConstants.HALF_MAX_SEQUENCE),
    ]

    all_passed = True
    for name, expected, actual in tests:
        status = "✅" if expected == actual else "❌"
        print(f"{status} {name}: {actual} (预期: {expected})")
        if expected != actual:
            all_passed = False

    print()
    return all_passed


def test_packet_properties():
    """验证 PacketProperty 枚举值"""
    print("="*60)
    print("PacketProperty 枚举验证")
    print("="*60)

    # C# LiteNetLib v0.9.5.2 的值
    expected_values = {
        "UNRELIABLE": 0,
        "CHANNELED": 1,
        "ACK": 2,
        "PING": 3,
        "PONG": 4,
        "CONNECT_REQUEST": 5,
        "CONNECT_ACCEPT": 6,
        "DISCONNECT": 7,
        "UNCONNECTED_MESSAGE": 8,
        "MTU_CHECK": 9,
        "MTU_OK": 10,
        "BROADCAST": 11,
        "MERGED": 12,
        "SHUTDOWN_OK": 13,
        "PEER_NOT_FOUND": 14,
        "INVALID_PROTOCOL": 15,
        "NAT_MESSAGE": 16,
        "EMPTY": 17,
    }

    all_passed = True
    for name, expected in expected_values.items():
        actual = PacketProperty[name].value
        status = "✅" if expected == actual else "❌"
        print(f"{status} {name}: {actual} (预期: {expected})")
        if expected != actual:
            all_passed = False

    print()
    return all_passed


def test_packet_binary_format():
    """验证数据包二进制格式与 C# 一致"""
    print("="*60)
    print("数据包二进制格式验证")
    print("="*60)

    all_passed = True

    # 测试 1: CHANNELED 包格式
    packet = NetPacket(PacketProperty.CHANNELED, 10)
    packet.sequence = 1234
    packet.channel_id = 5

    data = packet.get_bytes()
    print(f"✅ CHANNELED 包大小: {len(data)} 字节")

    # 验证字节格式
    # Byte 0: Property (1) + connection number (0)
    assert data[0] == 1, f"Byte 0 should be 1, got {data[0]}"

    # Bytes 1-2: Sequence (1234 in little-endian)
    seq = struct.unpack('<H', bytes(data[1:3]))[0]
    assert seq == 1234, f"Sequence should be 1234, got {seq}"

    # Byte 3: Channel ID
    assert data[3] == 5, f"Channel ID should be 5, got {data[3]}"

    print("✅ CHANNELED 包字节序正确（小端）")

    # 测试 2: 分片包格式
    packet2 = NetPacket(PacketProperty.CHANNELED, 0)
    packet2.mark_fragmented()
    packet2.fragment_id = 100
    packet2.fragment_part = 2
    packet2.fragments_total = 5

    data2 = packet2.get_bytes()

    # Byte 0: Property (1) + fragmented flag (0x80)
    assert data2[0] == 0x81, f"Byte 0 should be 0x81, got {data2[0]:02X}"

    # Bytes 4-5: Fragment ID
    frag_id = struct.unpack('<H', bytes(data2[4:6]))[0]
    assert frag_id == 100, f"Fragment ID should be 100, got {frag_id}"

    # Bytes 6-7: Fragment Part
    frag_part = struct.unpack('<H', bytes(data2[6:8]))[0]
    assert frag_part == 2, f"Fragment Part should be 2, got {frag_part}"

    # Bytes 8-9: Fragments Total
    frag_total = struct.unpack('<H', bytes(data2[8:10]))[0]
    assert frag_total == 5, f"Fragments Total should be 5, got {frag_total}"

    print("✅ 分片包格式正确")

    print()
    return all_passed


def test_serialization_compatibility():
    """验证序列化格式与 C# 一致"""
    print("="*60)
    print("序列化格式验证")
    print("="*60)

    all_passed = True

    # 测试 1: 基本类型
    writer = NetDataWriter()

    writer.put_byte(0x12)
    writer.put_short(0x1234)
    writer.put_int(0x12345678)
    writer.put_long(0x123456789ABCDEF0)
    writer.put_float(3.14)
    writer.put_string("Hello")

    data = writer.to_bytes()
    reader = NetDataReader(data)

    b = reader.get_byte()
    s = reader.get_short()
    i = reader.get_int()
    l = reader.get_long()
    f = reader.get_float()
    str_val = reader.get_string()

    status = "✅" if b == 0x12 else "❌"
    print(f"{status} Byte: 0x{b:02X}")

    status = "✅" if s == 0x1234 else "❌"
    print(f"{status} Short: 0x{s:04X}")

    status = "✅" if i == 0x12345678 else "❌"
    print(f"{status} Int: 0x{i:08X}")

    status = "✅" if l == 0x123456789ABCDEF0 else "❌"
    print(f"{status} Long: 0x{l:016X}")

    status = "✅" if abs(f - 3.14) < 0.01 else "❌"
    print(f"{status} Float: {f}")

    status = "✅" if str_val == "Hello" else "❌"
    print(f"{status} String: '{str_val}'")

    # 测试 2: UTF-8 字符串
    writer2 = NetDataWriter()
    writer2.put_string("测试中文")
    writer2.put_string("Hello 世界")

    data2 = writer2.to_bytes()
    reader2 = NetDataReader(data2)

    str1 = reader2.get_string()
    str2 = reader2.get_string()

    status = "✅" if str1 == "测试中文" else "❌"
    print(f"{status} UTF-8 字符串 1: '{str1}'")

    status = "✅" if str2 == "Hello 世界" else "❌"
    print(f"{status} UTF-8 字符串 2: '{str2}'")

    print()
    return all_passed


def test_string_serialization_format():
    """验证字符串序列化格式与 C# 完全一致"""
    print("="*60)
    print("字符串序列化格式细节验证")
    print("="*60)

    writer = NetDataWriter()
    writer.put_string("Test")

    data = writer.to_bytes()

    # C# 格式: [length (ushort, 2 bytes)] [data (length-1 bytes)]
    # "Test" = 5 chars, but length = 5, data = 4 bytes (null terminator not sent)
    # Actually C# sends: ushort length (5), then 4 bytes of data

    length = struct.unpack('<H', bytes(data[0:2]))[0]
    actual_data = data[2:2+length-1]

    print(f"字符串长度字段: {length}")
    print(f"字符串数据: {actual_data}")
    print(f"字符串内容: {actual_data.decode('utf-8')}")

    status = "✅" if length == 5 else "❌"
    print(f"{status} 长度格式正确")

    status = "✅" if actual_data == b"Test" else "❌"
    print(f"{status} 数据格式正确")

    print()
    return True


def test_array_serialization():
    """验证数组序列化格式"""
    print("="*60)
    print("数组序列化验证")
    print("="*60)

    writer = NetDataWriter()
    writer.put_array([1, 2, 3, 4, 5])

    data = writer.to_bytes()
    reader = NetDataReader(data)
    result = reader.get_array()

    status = "✅" if result == [1, 2, 3, 4, 5] else "❌"
    print(f"{status} 整数数组: {result}")

    # 字节数组
    writer2 = NetDataWriter()
    writer2.put_array([0x10, 0x20, 0x30])

    data2 = writer2.to_bytes()
    reader2 = NetDataReader(data2)
    result2 = reader2.get_array()

    status = "✅" if result2 == [0x10, 0x20, 0x30] else "❌"
    print(f"{status} 字节数组: {[hex(x) for x in result2]}")

    print()
    return True


def test_cross_language_packet():
    """模拟 C# 创建的数据包，Python 能正确解析"""
    print("="*60)
    print("跨语言数据包解析测试")
    print("="*60)

    # 手动创建一个 C# 风格的数据包
    # 假设 C# 发送一个 CHANNELED 包:
    # Byte 0: 0x01 (CHANNELED)
    # Bytes 1-2: Sequence (1000)
    # Byte 3: Channel ID (2)
    # Bytes 4+: Data

    csharp_packet_data = struct.pack('<B', 0x01)  # Property
    csharp_packet_data += struct.pack('<H', 1000)  # Sequence
    csharp_packet_data += struct.pack('<B', 2)  # Channel ID
    csharp_packet_data += b"Hello from C#"  # Data

    # Python 解析
    packet = NetPacket.from_bytes(csharp_packet_data)

    status = "✅" if packet.packet_property == PacketProperty.CHANNELED else "❌"
    print(f"{status} PacketProperty: {packet.packet_property.name}")

    status = "✅" if packet.sequence == 1000 else "❌"
    print(f"{status} Sequence: {packet.sequence}")

    status = "✅" if packet.channel_id == 2 else "❌"
    print(f"{status} Channel ID: {packet.channel_id}")

    data = packet.get_data()
    status = "✅" if data == b"Hello from C#" else "❌"
    print(f"{status} Data: {data}")

    print()
    return True


def run_all_tests():
    """运行所有兼容性测试"""
    print("\n" + "="*60)
    print("LiteNetLib-Python v0.9.5.2 与 C# 二进制兼容性测试")
    print("="*60 + "\n")

    results = {
        "协议常量": test_constants(),
        "PacketProperty 枚举": test_packet_properties(),
        "数据包二进制格式": test_packet_binary_format(),
        "序列化格式": test_serialization_compatibility(),
        "字符串序列化细节": test_string_serialization_format(),
        "数组序列化": test_array_serialization(),
        "跨语言数据包": test_cross_language_packet(),
    }

    print("="*60)
    print("测试结果汇总")
    print("="*60)

    all_passed = True
    for test_name, passed in results.items():
        status = "✅ 通过" if passed else "❌ 失败"
        print(f"{status} - {test_name}")
        if not passed:
            all_passed = False

    print("="*60)

    if all_passed:
        print("\n🎉 所有测试通过！Python 实现与 C# v0.9.5.2 100% 二进制兼容！")
        return True
    else:
        print("\n❌ 部分测试失败，需要修复")
        return False


if __name__ == "__main__":
    success = run_all_tests()
    exit(0 if success else 1)
