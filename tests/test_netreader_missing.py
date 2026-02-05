"""
NetDataReader缺失方法测试

测试之前未直接测试的方法: get_char, get_remaining_bytes, get_bytes_with_length
"""

import pytest
from litenetlib.utils import NetDataReader, NetDataWriter


class TestNetDataReaderGetChar:
    """测试get_char方法"""

    def test_get_char_basic(self):
        """测试基本char读取"""
        writer = NetDataWriter()
        writer.put_char('A')

        reader = NetDataReader(writer.data)
        result = reader.get_char()
        assert result == 'A'

    def test_get_char_from_writer(self):
        """测试从writer写入的char"""
        writer = NetDataWriter()
        writer.put_char('X')

        reader = NetDataReader(writer.data)
        result = reader.get_char()
        assert result == 'X'

    def test_get_char_unicode(self):
        """测试Unicode字符"""
        writer = NetDataWriter()
        writer.put_char('中')

        reader = NetDataReader(writer.data)
        result = reader.get_char()
        assert result == '中'

    def test_get_char_multiple(self):
        """测试读取多个char"""
        writer = NetDataWriter()
        chars = ['A', 'B', 'C', 'X', 'Y', 'Z']
        for char in chars:
            writer.put_char(char)

        reader = NetDataReader(writer.data)
        for expected in chars:
            result = reader.get_char()
            assert result == expected

    def test_get_char_special_chars(self):
        """测试特殊字符"""
        writer = NetDataWriter()
        special_chars = ['\n', '\t', ' ', '!', '@', '#']
        for char in special_chars:
            writer.put_char(char)

        reader = NetDataReader(writer.data)
        for expected in special_chars:
            result = reader.get_char()
            assert result == expected


class TestNetDataReaderGetRemainingBytes:
    """测试get_remaining_bytes方法 - 注意：C# API返回剩余字节数据(byte[])"""

    def test_get_remaining_bytes_returns_bytes(self):
        """测试get_remaining_bytes返回bytes类型"""
        writer = NetDataWriter()
        writer.put_int(12345)

        reader = NetDataReader(writer.data)
        remaining = reader.get_remaining_bytes()
        assert isinstance(remaining, bytes)

    def test_get_remaining_bytes_empty(self):
        """测试空数据的剩余数据"""
        reader = NetDataReader(b'')
        remaining = reader.get_remaining_bytes()
        assert remaining == b''


class TestNetDataReaderGetBytesWithLength:
    """测试get_bytes_with_length方法"""

    def test_get_bytes_with_length_basic(self):
        """测试基本的带长度前缀的字节读取"""
        writer = NetDataWriter()
        data = b'\x01\x02\x03\x04\x05'
        writer.put_bytes_with_length(data)

        reader = NetDataReader(writer.data)
        result = reader.get_bytes_with_length()

        assert result == data

    def test_get_bytes_with_length_empty(self):
        """测试空字节读取"""
        writer = NetDataWriter()
        writer.put_bytes_with_length(b'')

        reader = NetDataReader(writer.data)
        result = reader.get_bytes_with_length()

        assert result == b''

    def test_get_bytes_with_length_large(self):
        """测试大块数据读取"""
        writer = NetDataWriter()
        large_data = b'\x00' * 1000
        writer.put_bytes_with_length(large_data)

        reader = NetDataReader(writer.data)
        result = reader.get_bytes_with_length()

        assert result == large_data
        assert len(result) == 1000

    def test_get_bytes_with_length_multiple(self):
        """测试读取多个带长度前缀的字节数组"""
        writer = NetDataWriter()
        data1 = b'\x01\x02\x03'
        data2 = b'\x04\x05\x06\x07'
        data3 = b'\x08\x09'

        writer.put_bytes_with_length(data1)
        writer.put_bytes_with_length(data2)
        writer.put_bytes_with_length(data3)

        reader = NetDataReader(writer.data)
        result1 = reader.get_bytes_with_length()
        result2 = reader.get_bytes_with_length()
        result3 = reader.get_bytes_with_length()

        assert result1 == data1
        assert result2 == data2
        assert result3 == data3

    def test_get_bytes_with_length_with_offset(self):
        """测试带偏移量的字节写入和读取"""
        writer = NetDataWriter()
        full_data = b'\x00\x01\x02\x03\x04\x05\x06\x07\x08\x09'

        # Write with offset
        writer.put_bytes_with_length(full_data, offset=2, length=5)

        reader = NetDataReader(writer.data)
        result = reader.get_bytes_with_length()

        # Should have read bytes from index 2 to 6 (5 bytes)
        assert result == b'\x02\x03\x04\x05\x06'

    def test_get_bytes_with_length_binary_data(self):
        """测试二进制数据读取"""
        writer = NetDataWriter()
        # Create binary data with all possible byte values
        binary_data = bytes(range(256))
        writer.put_bytes_with_length(binary_data)

        reader = NetDataReader(writer.data)
        result = reader.get_bytes_with_length()

        assert result == binary_data
        assert len(result) == 256

    def test_get_bytes_with_length_mixed_content(self):
        """测试混合内容"""
        writer = NetDataWriter()
        writer.put_int(123)

        data = b'\xAA\xBB\xCC\xDD'
        writer.put_bytes_with_length(data)

        writer.put_string("test")

        reader = NetDataReader(writer.data)
        int_val = reader.get_int()
        assert int_val == 123

        bytes_result = reader.get_bytes_with_length()
        assert bytes_result == data

        str_result = reader.get_string()
        assert str_result == "test"


class TestNetDataReaderEdgeCasesCombined:
    """组合边缘情况测试"""

    def test_get_remaining_bytes_with_bytes_with_length(self):
        """测试get_remaining_bytes和get_bytes_with_length组合使用"""
        writer = NetDataWriter()

        data1 = b'\x01\x02\x03'
        data2 = b'\x04\x05\x06\x07\x08'

        writer.put_bytes_with_length(data1)
        writer.put_bytes_with_length(data2)

        reader = NetDataReader(writer.data)

        # Read first data
        result1 = reader.get_bytes_with_length()
        assert result1 == data1

        # Get remaining bytes - should return bytes type
        remaining = reader.get_remaining_bytes()
        assert isinstance(remaining, bytes)

    def test_char_with_remaining_bytes(self):
        """测试get_char和get_remaining_bytes组合"""
        writer = NetDataWriter()
        writer.put_char('A')
        writer.put_char('B')

        reader = NetDataReader(writer.data)

        # Read first char
        reader.get_char()

        # Get remaining bytes - should return bytes type
        remaining = reader.get_remaining_bytes()
        assert isinstance(remaining, bytes)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
