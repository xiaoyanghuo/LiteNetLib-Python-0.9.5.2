"""
NetDataReader and NetDataWriter 完整测试

对应C#测试: LiteNetLib.Tests/ReaderWriterSimpleDataTest.cs (300行)
测试所有数据类型的序列化/反序列化，包括数组类型
"""

import unittest
import sys
sys.path.insert(0, '.')

from litenetlib.utils import NetDataReader, NetDataWriter


class TestDataReaderWriterBasicTypes(unittest.TestCase):
    """测试基本数据类型 - 对应C# ReaderWriterSimpleDataTest.cs"""

    def test_write_read_bool(self):
        """对应C#: WriteReadBool()"""
        writer = NetDataWriter()
        writer.put_bool(True)
        writer.put_bool(False)

        reader = NetDataReader()
        reader.set_source(writer.data, 0, writer.length)

        self.assertTrue(reader.get_bool())
        self.assertFalse(reader.get_bool())

    def test_write_read_short(self):
        """对应C#: WriteReadShort()"""
        writer = NetDataWriter()
        test_values = [0, 1, -1, 32767, -32768, 12345, -12345]
        for val in test_values:
            writer.put_short(val)

        reader = NetDataReader()
        reader.set_source(writer.data, 0, writer.length)

        for expected in test_values:
            self.assertEqual(expected, reader.get_short())

    def test_write_read_int(self):
        """对应C#: 测试int类型（在WriteReadLong等测试中覆盖）"""
        writer = NetDataWriter()
        test_values = [0, 1, -1, 2147483647, -2147483648, 123456789]
        for val in test_values:
            writer.put_int(val)

        reader = NetDataReader()
        reader.set_source(writer.data, 0, writer.length)

        for expected in test_values:
            self.assertEqual(expected, reader.get_int())

    def test_write_read_long(self):
        """对应C#: WriteReadLong()"""
        writer = NetDataWriter()
        test_values = [0, 1, -1, 9223372036854775807, -9223372036854775808]
        for val in test_values:
            writer.put_long(val)

        reader = NetDataReader()
        reader.set_source(writer.data, 0, writer.length)

        for expected in test_values:
            self.assertEqual(expected, reader.get_long())

    def test_write_read_float(self):
        """对应C#: WriteReadFloat()"""
        writer = NetDataWriter()
        test_values = [0.0, 1.5, -1.5, 3.14159, 1.23456789]
        for val in test_values:
            writer.put_float(val)

        reader = NetDataReader()
        reader.set_source(writer.data, 0, writer.length)

        for expected in test_values:
            result = reader.get_float()
            self.assertAlmostEqual(expected, result, places=5)

    def test_write_read_double(self):
        """对应C#: WriteReadDouble()"""
        writer = NetDataWriter()
        test_values = [0.0, 1.5, -1.5, 3.141592653589793, 1.234567890123456]
        for val in test_values:
            writer.put_double(val)

        reader = NetDataReader()
        reader.set_source(writer.data, 0, writer.length)

        for expected in test_values:
            result = reader.get_double()
            self.assertAlmostEqual(expected, result, places=10)

    def test_write_read_string(self):
        """对应C#: 测试字符串（在StringArray测试中覆盖）"""
        writer = NetDataWriter()
        test_strings = [
            "",
            "Hello",
            "Hello, World!",
            "测试中文",
            "Special chars: !@#$%^&*()",
            "A" * 1000  # 长字符串
        ]
        for s in test_strings:
            writer.put_string(s)

        reader = NetDataReader()
        reader.set_source(writer.data, 0, writer.length)

        for expected in test_strings:
            self.assertEqual(expected, reader.get_string())

    def test_write_read_net_endpoint(self):
        """对应C#: WriteReadNetEndPoint()"""
        writer = NetDataWriter()
        test_endpoints = [
            ("127.0.0.1", 9050),
            ("192.168.1.1", 8080),
            ("10.0.0.1", 12345),
        ]
        for ip, port in test_endpoints:
            writer.put_endpoint((ip, port))

        reader = NetDataReader()
        reader.set_source(writer.data, 0, writer.length)

        for expected_ip, expected_port in test_endpoints:
            endpoint = reader.get_net_endpoint()
            # endpoint is a tuple (address, port)
            self.assertEqual(expected_ip, endpoint[0])
            self.assertEqual(expected_port, endpoint[1])


class TestDataReaderWriterArrays(unittest.TestCase):
    """测试数组类型 - 对应C# ReaderWriterSimpleDataTest.cs数组测试"""

    def test_write_read_bool_array(self):
        """对应C#: WriteReadBoolArray()"""
        writer = NetDataWriter()
        test_arrays = [
            [],
            [True],
            [False],
            [True, False, True, False],
            [True] * 100,
            [False] * 100
        ]
        for arr in test_arrays:
            writer.put_bool_array(arr)

        reader = NetDataReader()
        reader.set_source(writer.data, 0, writer.length)

        for expected in test_arrays:
            result = reader.get_bool_array()
            self.assertEqual(expected, result)

    def test_write_read_short_array(self):
        """对应C#: WriteReadShortArray()"""
        writer = NetDataWriter()
        test_arrays = [
            [],
            [0, 1, -1, 32767, -32768],
            [100, -100, 1000, -1000],
            list(range(100))
        ]
        for arr in test_arrays:
            writer.put_short_array(arr)

        reader = NetDataReader()
        reader.set_source(writer.data, 0, writer.length)

        for expected in test_arrays:
            result = reader.get_short_array()
            self.assertEqual(expected, result)

    def test_write_read_int_array(self):
        """对应C#: WriteReadIntArray()"""
        writer = NetDataWriter()
        test_arrays = [
            [],
            [0, 1, -1, 2147483647, -2147483648],
            [100000, -100000, 123456789],
            list(range(100))
        ]
        for arr in test_arrays:
            writer.put_int_array(arr)

        reader = NetDataReader()
        reader.set_source(writer.data, 0, writer.length)

        for expected in test_arrays:
            result = reader.get_int_array()
            self.assertEqual(expected, result)

    def test_write_read_long_array(self):
        """对应C#: WriteReadLongArray()"""
        writer = NetDataWriter()
        test_arrays = [
            [],
            [0, 1, -1, 9223372036854775807, -9223372036854775808],
            [10000000000, -10000000000],
            list(range(50))
        ]
        for arr in test_arrays:
            writer.put_long_array(arr)

        reader = NetDataReader()
        reader.set_source(writer.data, 0, writer.length)

        for expected in test_arrays:
            result = reader.get_long_array()
            self.assertEqual(expected, result)

    def test_write_read_float_array(self):
        """对应C#: WriteReadFloatArray()"""
        writer = NetDataWriter()
        test_arrays = [
            [],
            [0.0, 1.5, -1.5, 3.14159],
            [1.1, 2.2, 3.3, 4.4, 5.5],
            [i * 0.1 for i in range(50)]
        ]
        for arr in test_arrays:
            writer.put_float_array(arr)

        reader = NetDataReader()
        reader.set_source(writer.data, 0, writer.length)

        for expected in test_arrays:
            result = reader.get_float_array()
            for exp, res in zip(expected, result):
                self.assertAlmostEqual(exp, res, places=5)

    def test_write_read_double_array(self):
        """对应C#: WriteReadDoubleArray()"""
        writer = NetDataWriter()
        test_arrays = [
            [],
            [0.0, 1.5, -1.5, 3.141592653589793],
            [1.1, 2.2, 3.3, 4.4, 5.5],
            [i * 0.1 for i in range(50)]
        ]
        for arr in test_arrays:
            writer.put_double_array(arr)

        reader = NetDataReader()
        reader.set_source(writer.data, 0, writer.length)

        for expected in test_arrays:
            result = reader.get_double_array()
            for exp, res in zip(expected, result):
                self.assertAlmostEqual(exp, res, places=10)

    def test_write_read_string_array(self):
        """对应C#: WriteReadStringArray()"""
        writer = NetDataWriter()
        test_arrays = [
            [],
            ["hello"],
            ["hello", "world", "test"],
            ["", "a", "ab", "abc"],
            ["中文", "test", "混合"],
            ["string" + str(i) for i in range(100)]
        ]
        for arr in test_arrays:
            writer.put_string_array(arr)

        reader = NetDataReader()
        reader.set_source(writer.data, 0, writer.length)

        for expected in test_arrays:
            result = reader.get_string_array()
            self.assertEqual(expected, result)

    def test_sized_array_test(self):
        """对应C#: SizedArrayTest() - 测试不同大小的数组"""
        writer = NetDataWriter()

        # 写入不同长度的数组
        test_sizes_and_data = [(0, b""), (1, b"\x00"), (10, bytes(range(10))), (100, bytes([i % 256 for i in range(100)]))]
        for size, data in test_sizes_and_data:
            # For byte arrays, we use put_bytes_with_length
            writer.put_bytes_with_length(data)

        reader = NetDataReader()
        reader.set_source(writer.data, 0, writer.length)

        for size, expected in test_sizes_and_data:
            result = reader.get_bytes_with_length()
            self.assertEqual(len(expected), len(result), f"Size mismatch for size={size}")
            self.assertEqual(expected, result, f"Data mismatch for size={size}")


class TestDataReaderWriterEdgeCases(unittest.TestCase):
    """测试边缘情况"""

    def test_empty_data(self):
        """测试空数据"""
        writer = NetDataWriter()
        self.assertEqual(0, writer.length)

        reader = NetDataReader()
        reader.set_source(writer.data, 0, 0)
        self.assertEqual(0, reader.available_bytes)

    def test_large_data(self):
        """测试大数据"""
        writer = NetDataWriter()
        large_size = 100000
        for i in range(large_size):
            writer.put_int(i)

        reader = NetDataReader()
        reader.set_source(writer.data, 0, writer.length)

        for i in range(large_size):
            self.assertEqual(i, reader.get_int())

    def test_mixed_types(self):
        """测试混合类型"""
        writer = NetDataWriter()
        writer.put_bool(True)
        writer.put_byte(42)
        writer.put_short(1000)
        writer.put_int(123456)
        writer.put_long(9876543210)
        writer.put_float(3.14)
        writer.put_double(2.718281828)
        writer.put_string("test")

        reader = NetDataReader()
        reader.set_source(writer.data, 0, writer.length)

        self.assertTrue(reader.get_bool())
        self.assertEqual(42, reader.get_byte())
        self.assertEqual(1000, reader.get_short())
        self.assertEqual(123456, reader.get_int())
        self.assertEqual(9876543210, reader.get_long())
        self.assertAlmostEqual(3.14, reader.get_float(), places=5)
        self.assertAlmostEqual(2.718281828, reader.get_double(), places=10)
        self.assertEqual("test", reader.get_string())


def run_tests():
    """运行所有测试"""
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    suite.addTests(loader.loadTestsFromTestCase(TestDataReaderWriterBasicTypes))
    suite.addTests(loader.loadTestsFromTestCase(TestDataReaderWriterArrays))
    suite.addTests(loader.loadTestsFromTestCase(TestDataReaderWriterEdgeCases))

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
