"""
CRC32C Layer 功能测试

对应C#测试: LiteNetLib.Tests/CRC32LayerTest.cs (93行)
测试CRC32C校验层的功能
"""

import unittest
import sys
sys.path.insert(0, '.')

from litenetlib.layers import Crc32cLayer
from litenetlib.utils import CRC32C


class TestCRC32Layer(unittest.TestCase):
    """测试CRC32C层 - 对应C# CRC32LayerTest.cs"""

    def setUp(self):
        """设置测试"""
        self.layer = Crc32cLayer()

    def test_returns_nil_count_for_too_short_message(self):
        """
        对应C#: ReturnsNilCountForTooShortMessage()

        测试过短消息（小于4字节）应该返回False
        CRC32校验和需要4字节
        """
        # 测试各种过短的消息
        for length in range(4):
            packet_data = bytearray(b"A" * length)
            result = self.layer.process_in_bound_packet(packet_data, 0, length)

            # C#行为：过短消息返回False
            self.assertFalse(result, f"Message length {length} should return False")

    def test_can_send_and_receive_same_message(self):
        """
        对应C#: CanSendAndReceiveSameMessage()

        测试完整的发送和接收流程
        """
        # 准备测试数据（使用较长的数据以产生不同的校验和）
        test_messages = [
            b"Hello World, this is a test message",
            b"Different test message with more content",
            b"Binary data: \x00\x01\x02\x03\x04\x05\x06\x07",
            b"A" * 100,  # 100 bytes of A
        ]

        for original_msg in test_messages:
            # 模拟发送：添加CRC32校验和
            data_to_send = bytearray(original_msg + b"\x00\x00\x00\x00")
            self.layer.process_out_bound_packet(data_to_send, 0, len(original_msg))

            # 模拟接收：验证CRC32校验和
            result = self.layer.process_in_bound_packet(data_to_send, 0, len(data_to_send))

            # 应该成功验证
            self.assertTrue(result, f"Should successfully verify valid data: {original_msg[:20]}...")

    def test_returns_nil_count_for_bad_checksum(self):
        """
        对应C#: ReturnsNilCountForBadChecksum()

        测试错误校验和应该返回False
        """
        # 准备测试数据
        test_data = b"This is a longer test message to ensure proper checksum computation"
        original_data = bytearray(test_data)

        # 扩展4字节用于校验和
        data_with_checksum = original_data + b"\x00\x00\x00\x00"

        # ProcessOutBoundPacket添加CRC32校验和（修改in-place）
        self.layer.process_out_bound_packet(data_with_checksum, 0, len(original_data))

        # 验证当前校验和正确
        self.assertTrue(self.layer.process_in_bound_packet(data_with_checksum, 0, len(data_with_checksum)),
                       "Original checksum should be valid")

        # 篡改数据以破坏校验和
        data_with_checksum[10] = (data_with_checksum[10] + 1) % 256

        # ProcessInBoundPacket应该检测到校验和错误并返回False
        result = self.layer.process_in_bound_packet(data_with_checksum, 0, len(data_with_checksum))
        self.assertFalse(result, "Corrupted data should return False")


class TestCRC32LayerDetailed(unittest.TestCase):
    """CRC32C层详细测试"""

    def setUp(self):
        """设置测试"""
        self.layer = Crc32cLayer()

    def test_checksum_size(self):
        """测试校验和大小为4字节"""
        # 准备测试数据
        original_data = b"Test data for checksum"
        packet_data = bytearray(original_data + b"\x00\x00\x00\x00")

        # ProcessOutBoundPacket添加校验和
        self.layer.process_out_bound_packet(packet_data, 0, len(original_data))

        # 校验和已经被写入最后4字节
        checksum_bytes = packet_data[-4:]
        self.assertEqual(4, len(checksum_bytes))

    def test_checksum_consistency(self):
        """测试校验和计算的一致性"""
        # 准备测试数据
        test_data = b"Consistent test data for checksum"
        packet_data = bytearray(test_data + b"\x00\x00\x00\x00")

        # 多次计算应该得到相同的校验和
        checksums = []
        for _ in range(5):
            packet_copy = bytearray(test_data + b"\x00\x00\x00\x00")
            self.layer.process_out_bound_packet(packet_copy, 0, len(test_data))
            # 提取校验和（最后4字节）
            checksum = packet_copy[-4:]
            checksums.append(checksum)

        # 所有结果应该相同
        for checksum in checksums[1:]:
            self.assertEqual(checksums[0], checksum)

    def test_different_data_different_checksum(self):
        """测试不同数据产生不同校验和"""
        # 使用较长的数据以确保产生不同的校验和
        test_messages = [
            b"First message with some content",
            b"Second message with different content",
            b"Third message that is unique",
        ]

        checksums = []
        for msg in test_messages:
            packet_data = bytearray(msg + b"\x00\x00\x00\x00")
            self.layer.process_out_bound_packet(packet_data, 0, len(msg))
            # 提取校验和（最后4字节）
            checksum = packet_data[-4:]
            checksums.append(checksum)

        # 所有校验和应该不同
        for i in range(len(checksums)):
            for j in range(i + 1, len(checksums)):
                self.assertNotEqual(checksums[i], checksums[j],
                                  f"Different data should produce different checksums")

    def test_corruption_detection(self):
        """测试检测数据损坏"""
        # 准备测试数据
        test_data = b"Important data for corruption detection test"
        packet_data = bytearray(test_data + b"\x00\x00\x00\x00")

        # 添加校验和
        self.layer.process_out_bound_packet(packet_data, 0, len(test_data))

        # 在不同位置篡改数据
        corruption_positions = [0, len(test_data) // 2, len(test_data) - 1]

        for pos in corruption_positions:
            # 创建副本并篡改
            corrupted_data = bytearray(packet_data)
            corrupted_data[pos] = (corrupted_data[pos] + 1) % 256

            # 应该检测到损坏
            result = self.layer.process_in_bound_packet(corrupted_data, 0, len(corrupted_data))
            self.assertFalse(result,
                           f"Should detect corruption at position {pos}")

    def test_round_trip_multiple_messages(self):
        """测试多消息往返"""
        messages = [
            b"First test message",
            b"Second test message",
            b"Third test message",
            b"Fourth test message",
            b"Fifth test message",
        ]

        for msg in messages:
            # 发送
            data_to_send = bytearray(msg + b"\x00\x00\x00\x00")
            self.layer.process_out_bound_packet(data_to_send, 0, len(msg))

            # 接收
            result = self.layer.process_in_bound_packet(data_to_send, 0, len(data_to_send))

            # 验证
            self.assertTrue(result)


def run_tests():
    """运行所有测试"""
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    suite.addTests(loader.loadTestsFromTestCase(TestCRC32Layer))
    suite.addTests(loader.loadTestsFromTestCase(TestCRC32LayerDetailed))

    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    print("\n" + "=" * 60)
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print("=" * 60)

    return 0 if result.wasSuccessful() else 1


if __name__ == "__main__":
    sys.exit(run_tests())
