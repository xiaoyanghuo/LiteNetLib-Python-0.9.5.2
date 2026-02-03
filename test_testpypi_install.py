"""
TestPyPI 安装包完整测试
测试从 TestPyPI 安装的 litenetlib-0952 包的所有功能
"""

import sys
import asyncio
import io

# Fix UTF-8 encoding on Windows
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')
from litenetlib.core.constants import (
    NetConstants, PacketProperty, DeliveryMethod,
    get_header_size, DisconnectReason
)
from litenetlib.core.packet import NetPacket, NetPacketPool
from litenetlib.core.manager import LiteNetManager
from litenetlib.core.events import EventBasedNetListener
from litenetlib.core.peer import NetPeer
from litenetlib.utils.data_writer import NetDataWriter
from litenetlib.utils.data_reader import NetDataReader
from litenetlib.utils.net_utils import NetUtils


def print_section(title):
    print("\n" + "="*70)
    print(f"  {title}")
    print("="*70)


def test_constants():
    """测试协议常量"""
    print_section("1. 协议常量测试")

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

    print(f"\n  结果: {passed}/{len(tests)} 通过")
    return passed == len(tests)


def test_packet_creation():
    """测试数据包创建"""
    print_section("2. 数据包创建测试")

    try:
        # 测试不同类型的数据包
        packets_created = []

        # Unreliable packet
        p1 = NetPacket(PacketProperty.UNRELIABLE, 100)
        assert p1.packet_property == PacketProperty.UNRELIABLE
        assert p1.size == 101
        packets_created.append("UNRELIABLE")

        # Channeled packet
        p2 = NetPacket(PacketProperty.CHANNELED, 50)
        assert p2.packet_property == PacketProperty.CHANNELED
        assert p2.size == 54  # 4 bytes header + 50 data
        assert p2.sequence == 0
        assert p2.channel_id == 0
        packets_created.append("CHANNELED")

        # ACK packet
        p3 = NetPacket(PacketProperty.ACK, 10)
        assert p3.packet_property == PacketProperty.ACK
        assert p3.size == 14  # 4 bytes header + 10 data
        packets_created.append("ACK")

        # MERGED packet
        p4 = NetPacket(PacketProperty.MERGED, 100)
        assert p4.packet_property == PacketProperty.MERGED
        packets_created.append("MERGED")

        print(f"  [PASS] 创建了 {len(packets_created)} 种类型的数据包")
        for p_type in packets_created:
            print(f"    - {p_type}")

        # 测试分片包
        p5 = NetPacket(PacketProperty.CHANNELED, 100)
        p5.mark_fragmented()
        p5.fragment_id = 1
        p5.fragment_part = 0
        p5.fragments_total = 5
        assert p5.is_fragmented
        assert p5.fragment_id == 1
        assert p5.fragment_part == 0
        assert p5.fragments_total == 5
        print(f"  [PASS] 分片包创建成功")

        # 测试数据包池
        pool = NetPacketPool()
        p6 = pool.get(100)
        assert p6.size == 100
        pool.recycle(p6)
        print(f"  [PASS] 数据包池工作正常")

        return True

    except Exception as e:
        print(f"  [FAIL] 数据包创建失败: {e}")
        return False


def test_serialization():
    """测试序列化功能"""
    print_section("3. 序列化功能测试")

    try:
        writer = NetDataWriter()

        # 基本类型
        writer.put_byte(0x12)
        writer.put_short(0x1234)
        writer.put_int(0x12345678)
        writer.put_long(0x123456789ABCDEF0)
        writer.put_float(3.14)
        writer.put_string("Hello TestPyPI!")
        writer.put_string("测试中文")

        # 读取
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
            ("Float", 3.14, round(f, 2)),
            ("String", "Hello TestPyPI!", str1),
            ("UTF-8", "测试中文", str2),
        ]

        passed = 0
        for name, expected, actual in tests:
            if expected == actual:
                print(f"  [PASS] {name}: {actual}")
                passed += 1
            else:
                print(f"  [FAIL] {name}: expected {expected}, got {actual}")

        # 测试数组
        writer2 = NetDataWriter()
        writer2.put_array([1, 2, 3, 4, 5])
        reader2 = NetDataReader(writer2.to_bytes())
        arr = reader2.get_array()

        if arr == [1, 2, 3, 4, 5]:
            print(f"  [PASS] 数组序列化: {arr}")
            passed += 1
        else:
            print(f"  [FAIL] 数组序列化: expected [1,2,3,4,5], got {arr}")

        print(f"\n  结果: {passed}/{len(tests) + 1} 通过")
        return passed == len(tests) + 1

    except Exception as e:
        print(f"  [FAIL] 序列化测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_packet_binary_format():
    """测试数据包二进制格式"""
    print_section("4. 数据包二进制格式测试")

    try:
        import struct

        # 创建 CHANNELED 包
        packet = NetPacket(PacketProperty.CHANNELED, 10)
        packet.sequence = 1234
        packet.channel_id = 5

        data = packet.get_bytes()

        # 验证字节格式
        tests = []

        # Byte 0: Property (1)
        if data[0] == 1:
            tests.append(("Property", "CHANNELED", "✓"))
        else:
            tests.append(("Property", f"Expected 1, got {data[0]}", "✗"))

        # Bytes 1-2: Sequence (1234 little-endian)
        seq = struct.unpack('<H', bytes(data[1:3]))[0]
        if seq == 1234:
            tests.append(("Sequence", f"{seq} (little-endian)", "✓"))
        else:
            tests.append(("Sequence", f"Expected 1234, got {seq}", "✗"))

        # Byte 3: Channel ID
        if data[3] == 5:
            tests.append(("Channel ID", "5", "✓"))
        else:
            tests.append(("Channel ID", f"Expected 5, got {data[3]}", "✗"))

        for name, result, status in tests:
            print(f"  [{status}] {name}: {result}")

        all_passed = all("✓" in t[2] for t in tests)

        if all_passed:
            print(f"\n  [PASS] 二进制格式完全正确")
        else:
            print(f"\n  [FAIL] 二进制格式有问题")

        return all_passed

    except Exception as e:
        print(f"  [FAIL] 二进制格式测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_cross_language_compatibility():
    """测试跨语言兼容性（模拟 C# 数据包）"""
    print_section("5. C# 互操作性测试")

    try:
        import struct

        # 模拟 C# 创建的数据包
        csharp_packet = (
            struct.pack('<B', 0x01) +      # CHANNELED
            struct.pack('<H', 1000) +      # Sequence
            struct.pack('<B', 2) +         # Channel ID
            b"Data from C#"               # Payload
        )

        # Python 解析
        packet = NetPacket.from_bytes(csharp_packet)

        tests = [
            ("PacketProperty", PacketProperty.CHANNELED, packet.packet_property),
            ("Sequence", 1000, packet.sequence),
            ("ChannelID", 2, packet.channel_id),
            ("Data", b"Data from C#", packet.get_data()),
        ]

        passed = 0
        for name, expected, actual in tests:
            if expected == actual:
                print(f"  [PASS] {name}: {actual}")
                passed += 1
            else:
                print(f"  [FAIL] {name}: expected {expected}, got {actual}")

        print(f"\n  结果: {passed}/{len(tests)} 通过")
        print(f"  说明: Python 可以正确解析 C# 创建的数据包")
        return passed == len(tests)

    except Exception as e:
        print(f"  [FAIL] C# 互操作性测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_packet_verification():
    """测试数据包验证"""
    print_section("6. 数据包验证测试")

    try:
        # 有效数据包
        valid_packet = NetPacket(PacketProperty.CHANNELED, 10)
        assert valid_packet.verify() == True
        print(f"  [PASS] 有效数据包通过验证")

        # 无效大小的数据包
        invalid_packet = NetPacket(PacketProperty.CHANNELED, 0)
        invalid_packet._size = 2  # 小于头部大小
        assert invalid_packet.verify() == False
        print(f"  [PASS] 无效数据包被拒绝")

        # 分片数据包
        fragmented = NetPacket(PacketProperty.CHANNELED, 10)
        fragmented.mark_fragmented()
        assert fragmented.verify() == True
        print(f"  [PASS] 分片数据包通过验证")

        return True

    except Exception as e:
        print(f"  [FAIL] 数据包验证测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_network_utils():
    """测试网络工具函数"""
    print_section("7. 网络工具函数测试")

    try:
        # 测试相对序列号
        result = NetUtils.relative_sequence_number(100, 90)
        assert result == 10
        print(f"  [PASS] 相对序列号 (普通): {result}")

        # 测试序列号回绕 (大数相对于小数是"旧"的，应该返回负数)
        result2 = NetUtils.relative_sequence_number(32760, 100)
        assert result2 < 0  # 应该是负数（回绕）
        print(f"  [PASS] 相对序列号 (回绕): {result2}")

        # 测试地址解析
        host, port = NetUtils.parse_address("127.0.0.1:7777")
        assert host == "127.0.0.1"
        assert port == 7777
        print(f"  [PASS] IPv4 地址解析: {host}:{port}")

        # 测试地址格式化
        addr = NetUtils.format_address("::1", 7777)
        assert addr == "[::1]:7777"
        print(f"  [PASS] IPv6 地址格式化: {addr}")

        return True

    except Exception as e:
        print(f"  [FAIL] 网络工具测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    print("\n" + "="*70)
    print("  LiteNetLib-Python v0.9.5.2 TestPyPI 安装测试")
    print("  来源: https://test.pypi.org/")
    print("="*70)

    print("\n检查安装...")
    import litenetlib
    print(f"  安装路径: {litenetlib.__file__}")
    print(f"  版本: 0.9.5.2")

    results = []

    # 运行所有测试
    results.append(("协议常量", test_constants()))
    results.append(("数据包创建", test_packet_creation()))
    results.append(("序列化功能", test_serialization()))
    results.append(("二进制格式", test_packet_binary_format()))
    results.append(("C# 互操作性", test_cross_language_compatibility()))
    results.append(("数据包验证", test_packet_verification()))
    results.append(("网络工具", test_network_utils()))

    # 汇总结果
    print_section("测试结果汇总")

    total = len(results)
    passed = sum(1 for _, result in results if result)

    for name, result in results:
        status = "[PASS]" if result else "[FAIL]"
        print(f"  {status} {name}")

    print("\n" + "="*70)
    print(f"  总计: {passed}/{total} 测试组通过")

    if passed == total:
        print(f"  状态: ✅ 所有测试通过！")
        print(f"  结论: TestPyPI 安装包功能完全正常")
    else:
        print(f"  状态: ❌ 部分测试失败")
        print(f"  结论: 需要检查失败的测试")

    print("="*70 + "\n")

    return passed == total


if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n❌ 测试运行出错: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
