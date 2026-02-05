"""
FastBitConverter二进制验证测试

验证FastBitConverter的所有方法输出正确的二进制格式
"""

import pytest
import struct
from litenetlib.utils import FastBitConverter


class TestFastBitConverterInt16:
    """测试16位整数转换"""

    def test_get_bytes_int16_positive(self):
        """测试正数int16转换"""
        data = bytearray(2)
        value = 1000

        FastBitConverter.get_bytes_int16(data, 0, value)

        # Verify with struct (little endian)
        expected = struct.pack('<h', value)
        assert bytes(data[0:2]) == expected

    def test_get_bytes_int16_negative(self):
        """测试负数int16转换"""
        data = bytearray(2)
        value = -1000

        FastBitConverter.get_bytes_int16(data, 0, value)

        # Verify with struct
        expected = struct.pack('<h', value)
        assert bytes(data[0:2]) == expected

    def test_get_bytes_int16_max_min(self):
        """测试int16边界值"""
        data = bytearray(2)

        # Max value
        FastBitConverter.get_bytes_int16(data, 0, 32767)
        assert struct.unpack('<h', data[0:2])[0] == 32767

        # Min value
        FastBitConverter.get_bytes_int16(data, 0, -32768)
        assert struct.unpack('<h', data[0:2])[0] == -32768

    def test_get_bytes_int16_offset(self):
        """测试带偏移量的int16转换"""
        data = bytearray(10)
        value = 1234
        offset = 5

        FastBitConverter.get_bytes_int16(data, offset, value)

        # Verify at offset
        result = struct.unpack('<h', data[offset:offset+2])[0]
        assert result == value


class TestFastBitConverterUInt16:
    """测试无符号16位整数转换"""

    def test_get_bytes_uint16_positive(self):
        """测试正数uint16转换"""
        data = bytearray(2)
        value = 50000

        FastBitConverter.get_bytes_uint16(data, 0, value)

        # Verify with struct
        expected = struct.pack('<H', value)
        assert bytes(data[0:2]) == expected

    def test_get_bytes_uint16_max(self):
        """测试uint16最大值"""
        data = bytearray(2)
        value = 65535

        FastBitConverter.get_bytes_uint16(data, 0, value)

        assert struct.unpack('<H', data[0:2])[0] == 65535

    def test_get_bytes_uint16_zero(self):
        """测试uint16零值"""
        data = bytearray(2)
        value = 0

        FastBitConverter.get_bytes_uint16(data, 0, value)

        assert data[0] == 0
        assert data[1] == 0


class TestFastBitConverterInt32:
    """测试32位整数转换"""

    def test_get_bytes_int32_positive(self):
        """测试正数int32转换"""
        data = bytearray(4)
        value = 1000000

        FastBitConverter.get_bytes_int32(data, 0, value)

        # Verify with struct
        expected = struct.pack('<i', value)
        assert bytes(data[0:4]) == expected

    def test_get_bytes_int32_negative(self):
        """测试负数int32转换"""
        data = bytearray(4)
        value = -1000000

        FastBitConverter.get_bytes_int32(data, 0, value)

        # Verify with struct
        expected = struct.pack('<i', value)
        assert bytes(data[0:4]) == expected

    def test_get_bytes_int32_max_min(self):
        """测试int32边界值"""
        data = bytearray(4)

        # Max value
        FastBitConverter.get_bytes_int32(data, 0, 2147483647)
        assert struct.unpack('<i', data[0:4])[0] == 2147483647

        # Min value
        FastBitConverter.get_bytes_int32(data, 0, -2147483648)
        assert struct.unpack('<i', data[0:4])[0] == -2147483648


class TestFastBitConverterUInt32:
    """测试无符号32位整数转换"""

    def test_get_bytes_uint32(self):
        """测试uint32转换"""
        data = bytearray(4)
        value = 3000000000

        FastBitConverter.get_bytes_uint32(data, 0, value)

        # Verify with struct
        expected = struct.pack('<I', value)
        assert bytes(data[0:4]) == expected

    def test_get_bytes_uint32_max(self):
        """测试uint32最大值"""
        data = bytearray(4)
        value = 4294967295

        FastBitConverter.get_bytes_uint32(data, 0, value)

        assert struct.unpack('<I', data[0:4])[0] == 4294967295


class TestFastBitConverterInt64:
    """测试64位整数转换"""

    def test_get_bytes_int64_positive(self):
        """测试正数int64转换"""
        data = bytearray(8)
        value = 1000000000000

        FastBitConverter.get_bytes_int64(data, 0, value)

        # Verify with struct
        expected = struct.pack('<q', value)
        assert bytes(data[0:8]) == expected

    def test_get_bytes_int64_negative(self):
        """测试负数int64转换"""
        data = bytearray(8)
        value = -1000000000000

        FastBitConverter.get_bytes_int64(data, 0, value)

        # Verify with struct
        expected = struct.pack('<q', value)
        assert bytes(data[0:8]) == expected

    def test_get_bytes_int64_max_min(self):
        """测试int64边界值"""
        data = bytearray(8)

        # Max value
        FastBitConverter.get_bytes_int64(data, 0, 9223372036854775807)
        assert struct.unpack('<q', data[0:8])[0] == 9223372036854775807

        # Min value
        FastBitConverter.get_bytes_int64(data, 0, -9223372036854775808)
        result = struct.unpack('<q', data[0:8])[0]
        assert result == -9223372036854775808


class TestFastBitConverterUInt64:
    """测试无符号64位整数转换"""

    def test_get_bytes_uint64(self):
        """测试uint64转换"""
        data = bytearray(8)
        value = 15000000000000000000

        FastBitConverter.get_bytes_uint64(data, 0, value)

        # Verify with struct
        expected = struct.pack('<Q', value)
        assert bytes(data[0:8]) == expected

    def test_get_bytes_uint64_max(self):
        """测试uint64最大值"""
        data = bytearray(8)
        value = 18446744073709551615

        FastBitConverter.get_bytes_uint64(data, 0, value)

        result = struct.unpack('<Q', data[0:8])[0]
        assert result == 18446744073709551615


class TestFastBitConverterFloat:
    """测试浮点数转换"""

    def test_get_bytes_float_positive(self):
        """测试正浮点数转换"""
        data = bytearray(4)
        value = 123.456

        FastBitConverter.get_bytes_float(data, 0, value)

        # Verify with struct
        expected = struct.pack('<f', value)
        result_bytes = bytes(data[0:4])

        # Float comparison needs tolerance
        result_val = struct.unpack('<f', result_bytes)[0]
        expected_val = struct.unpack('<f', expected)[0]
        assert abs(result_val - expected_val) < 1e-6

    def test_get_bytes_float_negative(self):
        """测试负浮点数转换"""
        data = bytearray(4)
        value = -123.456

        FastBitConverter.get_bytes_float(data, 0, value)

        result_val = struct.unpack('<f', data[0:4])[0]
        # Float has limited precision, use larger tolerance
        assert abs(result_val - value) < 1e-4

    def test_get_bytes_float_special_values(self):
        """测试浮点数特殊值"""
        data = bytearray(4)

        # Zero
        FastBitConverter.get_bytes_float(data, 0, 0.0)
        assert struct.unpack('<f', data[0:4])[0] == 0.0

        # Infinity
        FastBitConverter.get_bytes_float(data, 0, float('inf'))
        result = struct.unpack('<f', data[0:4])[0]
        assert result == float('inf')

        # Negative infinity
        FastBitConverter.get_bytes_float(data, 0, float('-inf'))
        result = struct.unpack('<f', data[0:4])[0]
        assert result == float('-inf')


class TestFastBitConverterDouble:
    """测试双精度浮点数转换"""

    def test_get_bytes_double_positive(self):
        """测试正双精度浮点数转换"""
        data = bytearray(8)
        value = 123456.789012

        FastBitConverter.get_bytes_double(data, 0, value)

        # Verify with struct
        result_val = struct.unpack('<d', data[0:8])[0]
        assert abs(result_val - value) < 1e-12

    def test_get_bytes_double_negative(self):
        """测试负双精度浮点数转换"""
        data = bytearray(8)
        value = -123456.789012

        FastBitConverter.get_bytes_double(data, 0, value)

        result_val = struct.unpack('<d', data[0:8])[0]
        assert abs(result_val - value) < 1e-12

    def test_get_bytes_double_special_values(self):
        """测试双精度浮点数特殊值"""
        data = bytearray(8)

        # Zero
        FastBitConverter.get_bytes_double(data, 0, 0.0)
        assert struct.unpack('<d', data[0:8])[0] == 0.0

        # Infinity
        FastBitConverter.get_bytes_double(data, 0, float('inf'))
        result = struct.unpack('<d', data[0:8])[0]
        assert result == float('inf')

        # Negative infinity
        FastBitConverter.get_bytes_double(data, 0, float('-inf'))
        result = struct.unpack('<d', data[0:8])[0]
        assert result == float('-inf')


class TestFastBitConverterEndianness:
    """测试字节序"""

    def test_little_endian(self):
        """测试小端字节序"""
        data = bytearray(2)
        value = 0x1234

        FastBitConverter.get_bytes_int16(data, 0, value)

        # Little endian: low byte first
        assert data[0] == 0x34
        assert data[1] == 0x12

    def test_little_endian_int32(self):
        """测试int32小端字节序"""
        data = bytearray(4)
        value = 0x12345678

        FastBitConverter.get_bytes_int32(data, 0, value)

        # Little endian
        assert data[0] == 0x78
        assert data[1] == 0x56
        assert data[2] == 0x34
        assert data[3] == 0x12


class TestFastBitConverterMultipleValues:
    """测试连续写入多个值"""

    def test_multiple_int16(self):
        """测试连续写入多个int16"""
        data = bytearray(10)
        values = [100, 200, 300, 400, 500]

        for i, value in enumerate(values):
            FastBitConverter.get_bytes_int16(data, i * 2, value)

        for i, expected in enumerate(values):
            result = struct.unpack('<h', data[i*2:i*2+2])[0]
            assert result == expected

    def test_multiple_int32(self):
        """测试连续写入多个int32"""
        data = bytearray(16)
        values = [1000, 2000, 3000, 4000]

        for i, value in enumerate(values):
            FastBitConverter.get_bytes_int32(data, i * 4, value)

        for i, expected in enumerate(values):
            result = struct.unpack('<i', data[i*4:i*4+4])[0]
            assert result == expected

    def test_mixed_types(self):
        """测试混合类型写入"""
        data = bytearray(18)

        FastBitConverter.get_bytes_int16(data, 0, 100)
        FastBitConverter.get_bytes_int32(data, 2, 1000)
        FastBitConverter.get_bytes_int64(data, 6, 10000)
        FastBitConverter.get_bytes_float(data, 14, 1.5)

        assert struct.unpack('<h', data[0:2])[0] == 100
        assert struct.unpack('<i', data[2:6])[0] == 1000
        assert struct.unpack('<q', data[6:14])[0] == 10000
        assert abs(struct.unpack('<f', data[14:18])[0] - 1.5) < 1e-6


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
