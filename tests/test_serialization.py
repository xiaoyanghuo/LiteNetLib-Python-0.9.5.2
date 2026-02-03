"""
Serialization Tests / 序列化测试

Tests for DataWriter and DataReader classes including all data types,
endianness, and encoding.

Reference C# Code: LiteNetLib/Utils/NetDataWriter.cs and NetDataReader.cs
"""

import pytest
import struct
import uuid
from litenetlib.utils.data_writer import NetDataWriter
from litenetlib.utils.data_reader import NetDataReader


class TestDataWriterBasicTypes:
    """Test DataWriter basic type writing / 测试 DataWriter 基本类型写入"""

    def test_put_byte(self):
        """Test writing byte / 测试写入字节"""
        writer = NetDataWriter()
        writer.put_byte(42)
        assert writer.length == 1
        assert writer.data[0] == 42

    def test_put_byte_bounds(self):
        """Test byte bounds / 测试字节边界"""
        writer = NetDataWriter()
        writer.put_byte(0)
        writer.put_byte(255)
        assert writer.data[0] == 0
        assert writer.data[1] == 255

    def test_put_byte_masking(self):
        """Test byte is masked to 8 bits / 测试字节被屏蔽为 8 位"""
        writer = NetDataWriter()
        writer.put_byte(256)  # Should be masked to 0
        assert writer.data[0] == 0, \
            f"Byte 256 should be masked to 0, got {writer.data[0]}"

    def test_put_sbyte(self):
        """Test writing signed byte / 测试写入有符号字节"""
        writer = NetDataWriter()
        writer.put_sbyte(-128)
        writer.put_sbyte(127)
        assert writer.data[0] == 128  # -128 as unsigned byte
        assert writer.data[1] == 127

    def test_put_bool(self):
        """Test writing boolean / 测试写入布尔值"""
        writer = NetDataWriter()
        writer.put_bool(True)
        writer.put_bool(False)
        assert writer.data[0] == 1
        assert writer.data[1] == 0

    def test_put_short(self):
        """Test writing short (16-bit) / 测试写入短整型（16位）"""
        writer = NetDataWriter()
        writer.put_short(-1000)
        assert writer.length == 2
        # Check little-endian
        value = struct.unpack_from('<h', writer.data, 0)[0]
        assert value == -1000

    def test_put_ushort(self):
        """Test writing ushort (16-bit unsigned) / 测试写入无符号短整型"""
        writer = NetDataWriter()
        writer.put_ushort(50000)
        assert writer.length == 2
        value = struct.unpack_from('<H', writer.data, 0)[0]
        assert value == 50000

    def test_put_int(self):
        """Test writing int (32-bit) / 测试写入整型（32位）"""
        writer = NetDataWriter()
        writer.put_int(123456789)
        assert writer.length == 4
        value = struct.unpack_from('<i', writer.data, 0)[0]
        assert value == 123456789

    def test_put_uint(self):
        """Test writing uint (32-bit unsigned) / 测试写入无符号整型"""
        writer = NetDataWriter()
        writer.put_uint(4000000000)
        assert writer.length == 4
        value = struct.unpack_from('<I', writer.data, 0)[0]
        assert value == 4000000000

    def test_put_long(self):
        """Test writing long (64-bit) / 测试写入长整型（64位）"""
        writer = NetDataWriter()
        writer.put_long(-9007199254740992)
        assert writer.length == 8
        value = struct.unpack_from('<q', writer.data, 0)[0]
        assert value == -9007199254740992

    def test_put_ulong(self):
        """Test writing ulong (64-bit unsigned) / 测试写入无符号长整型"""
        writer = NetDataWriter()
        writer.put_ulong(18000000000000000000)
        assert writer.length == 8
        value = struct.unpack_from('<Q', writer.data, 0)[0]
        assert value == 18000000000000000000

    def test_put_float(self):
        """Test writing float (32-bit) / 测试写入浮点数（32位）"""
        writer = NetDataWriter()
        writer.put_float(3.14159)
        assert writer.length == 4
        value = struct.unpack_from('<f', writer.data, 0)[0]
        assert abs(value - 3.14159) < 0.00001

    def test_put_float_special_values(self):
        """Test writing special float values / 测试写入特殊浮点值"""
        writer = NetDataWriter()
        writer.put_float(float('inf'))
        writer.put_float(float('-inf'))
        writer.put_float(float('nan'))

        assert struct.unpack_from('<f', writer.data, 0)[0] == float('inf')
        assert struct.unpack_from('<f', writer.data, 4)[0] == float('-inf')
        # NaN comparison requires special handling
        import math
        assert math.isnan(struct.unpack_from('<f', writer.data, 8)[0])

    def test_put_double(self):
        """Test writing double (64-bit) / 测试写入双精度（64位）"""
        writer = NetDataWriter()
        writer.put_double(3.141592653589793)
        assert writer.length == 8
        value = struct.unpack_from('<d', writer.data, 0)[0]
        assert abs(value - 3.141592653589793) < 1e-15

    def test_put_char(self):
        """Test writing char / 测试写入字符"""
        writer = NetDataWriter()
        writer.put_char('A')
        assert writer.length == 2
        value = struct.unpack_from('<H', writer.data, 0)[0]
        assert value == ord('A')


class TestDataWriterStrings:
    """Test DataWriter string writing / 测试 DataWriter 字符串写入"""

    def test_put_empty_string(self):
        """Test writing empty string / 测试写入空字符串"""
        writer = NetDataWriter()
        writer.put_string("")
        assert writer.length == 2  # ushort length = 0
        assert writer.data[0] == 0
        assert writer.data[1] == 0

    def test_put_simple_string(self):
        """Test writing simple string / 测试写入简单字符串"""
        writer = NetDataWriter()
        writer.put_string("Hello")
        # Length prefix (2 bytes) + data (5 bytes)
        assert writer.length == 7
        # Length should be size + 1 for non-empty string
        assert writer.data[0] == 6  # 5 + 1
        assert writer.data[1] == 0

    def test_put_string_utf8(self):
        """Test writing UTF-8 string / 测试写入 UTF-8 字符串"""
        writer = NetDataWriter()
        writer.put_string("你好")  # Chinese characters
        # Should encode to UTF-8
        data = writer.to_bytes()
        reader = NetDataReader(data)
        result = reader.get_string()
        assert result == "你好"

    def test_put_string_with_max_length(self):
        """Test writing string with max length / 测试写入带最大长度限制的字符串"""
        writer = NetDataWriter()
        long_string = "a" * 100
        writer.put_string(long_string, max_length=10)
        # Should truncate to 10 characters
        data = writer.to_bytes()
        reader = NetDataReader(data)
        result = reader.get_string(max_length=10)
        assert result == "a" * 10

    def test_put_large_string(self):
        """Test writing large string with int length / 测试写入大字符串（int 长度前缀）"""
        writer = NetDataWriter()
        large_string = "x" * 100000
        writer.put_large_string(large_string)
        # Should use int length prefix (4 bytes)
        assert writer.length >= 100004  # 4 + 100000
        data = writer.to_bytes()
        reader = NetDataReader(data)
        result = reader.get_large_string()
        assert result == large_string


class TestDataWriterBytes:
    """Test DataWriter bytes writing / 测试 DataWriter 字节写入"""

    def test_put_bytes(self):
        """Test writing bytes / 测试写入字节"""
        writer = NetDataWriter()
        data = b'Hello World'
        writer.put_bytes(data)
        assert writer.length == len(data)
        assert writer.data[:len(data)] == data

    def test_put_bytes_with_offset(self):
        """Test writing bytes with offset / 测试写入带偏移量的字节"""
        writer = NetDataWriter()
        data = b'Hello World'
        writer.put_bytes(data, offset=6, length=5)
        assert writer.length == 5
        assert writer.data[:5] == b'World'

    def test_put_bytes_with_length(self):
        """Test writing partial bytes / 测试写入部分字节"""
        writer = NetDataWriter()
        data = b'Hello World'
        writer.put_bytes(data, length=5)
        assert writer.length == 5
        assert writer.data[:5] == b'Hello'

    def test_put_bytes_with_length_prefix(self):
        """Test writing bytes with length prefix / 测试写入带长度前缀的字节"""
        writer = NetDataWriter()
        data = b'Test Data'
        writer.put_bytes_with_length(data)
        assert writer.length == 2 + len(data)  # ushort + data
        reader = NetDataReader(writer.to_bytes())
        result = reader.get_bytes_with_length()
        assert result == data


class TestDataWriterArrays:
    """Test DataWriter array writing / 测试 DataWriter 数组写入"""

    def test_put_array_none(self):
        """Test writing None array / 测试写入 None 数组"""
        writer = NetDataWriter()
        writer.put_array(None)
        assert writer.length == 2  # ushort length = 0
        assert writer.data[0] == 0
        assert writer.data[1] == 0

    def test_put_array_empty(self):
        """Test writing empty array / 测试写入空数组"""
        writer = NetDataWriter()
        writer.put_array([])
        assert writer.length == 2

    def test_put_int_array(self):
        """Test writing int array / 测试写入整型数组"""
        writer = NetDataWriter()
        arr = [1, 2, 3, 4, 5]
        writer.put_array(arr, element_size=4)
        data = writer.to_bytes()
        reader = NetDataReader(data)
        result = reader.get_array(element_size=4)
        assert result == arr

    def test_put_byte_array(self):
        """Test writing byte array / 测试写入字节数组"""
        writer = NetDataWriter()
        arr = [1, 2, 3]
        writer.put_array(arr, element_size=1)
        data = writer.to_bytes()
        reader = NetDataReader(data)
        result = reader.get_array(element_size=1)
        assert result == arr

    def test_put_string_array(self):
        """Test writing string array / 测试写入字符串数组"""
        writer = NetDataWriter()
        arr = ["Hello", "World", "Test"]
        writer.put_string_array(arr)
        data = writer.to_bytes()
        reader = NetDataReader(data)
        result = reader.get_string_array()
        assert result == arr


class TestDataWriterSpecialTypes:
    """Test DataWriter special types / 测试 DataWriter 特殊类型"""

    def test_put_uuid(self):
        """Test writing UUID / 测试写入 UUID"""
        writer = NetDataWriter()
        test_uuid = uuid.uuid4()
        writer.put_uuid(test_uuid)
        assert writer.length == 16
        data = writer.to_bytes()
        reader = NetDataReader(data)
        result = reader.get_uuid()
        assert result == test_uuid

    def test_put_ip_end_point_ipv4(self):
        """Test writing IPv4 endpoint / 测试写入 IPv4 端点"""
        writer = NetDataWriter()
        writer.put_ip_end_point("192.168.1.1", 8080, 'IPv4')
        data = writer.to_bytes()
        reader = NetDataReader(data)
        address, port, family = reader.get_ip_end_point()
        assert address == "192.168.1.1"
        assert port == 8080
        assert family == 'IPv4'

    def test_put_ip_end_point_ipv6(self):
        """Test writing IPv6 endpoint / 测试写入 IPv6 端点"""
        writer = NetDataWriter()
        writer.put_ip_end_point("::1", 8080, 'IPv6')
        data = writer.to_bytes()
        reader = NetDataReader(data)
        address, port, family = reader.get_ip_end_point()
        assert address == "::1"
        assert port == 8080
        assert family == 'IPv6'


class TestDataWriterConvenience:
    """Test DataWriter convenience methods / 测试 DataWriter 便捷方法"""

    def test_put_auto_type(self):
        """Test automatic type detection / 测试自动类型检测"""
        writer = NetDataWriter()
        writer.put(True)  # bool
        writer.put(42)  # int
        writer.put(3.14)  # float
        writer.put("Hello")  # string
        writer.put(b"World")  # bytes

        assert writer.length > 0

    def test_from_string(self):
        """Test creating writer from string / 测试从字符串创建 writer"""
        writer = NetDataWriter.from_string("Test")
        data = writer.to_bytes()
        reader = NetDataReader(data)
        result = reader.get_string()
        assert result == "Test"

    def test_from_bytes(self):
        """Test creating writer from bytes / 测试从字节创建 writer"""
        original = b'Test Data'
        writer = NetDataWriter.from_bytes(original)
        assert writer.to_bytes() == original


class TestDataReaderBasicTypes:
    """Test DataReader basic type reading / 测试 DataReader 基本类型读取"""

    def test_get_byte(self):
        """Test reading byte / 测试读取字节"""
        data = struct.pack('<B', 42)
        reader = NetDataReader(data)
        assert reader.get_byte() == 42

    def test_get_sbyte(self):
        """Test reading signed byte / 测试读取有符号字节"""
        data = struct.pack('<b', -100)
        reader = NetDataReader(data)
        assert reader.get_sbyte() == -100

    def test_get_bool(self):
        """Test reading boolean / 测试读取布尔值"""
        data = struct.pack('<BB', 1, 0)
        reader = NetDataReader(data)
        assert reader.get_bool() is True
        assert reader.get_bool() is False

    def test_get_short(self):
        """Test reading short / 测试读取短整型"""
        data = struct.pack('<h', -1000)
        reader = NetDataReader(data)
        assert reader.get_short() == -1000

    def test_get_ushort(self):
        """Test reading ushort / 测试读取无符号短整型"""
        data = struct.pack('<H', 50000)
        reader = NetDataReader(data)
        assert reader.get_ushort() == 50000

    def test_get_int(self):
        """Test reading int / 测试读取整型"""
        data = struct.pack('<i', 123456789)
        reader = NetDataReader(data)
        assert reader.get_int() == 123456789

    def test_get_uint(self):
        """Test reading uint / 测试读取无符号整型"""
        data = struct.pack('<I', 4000000000)
        reader = NetDataReader(data)
        assert reader.get_uint() == 4000000000

    def test_get_long(self):
        """Test reading long / 测试读取长整型"""
        data = struct.pack('<q', -9007199254740992)
        reader = NetDataReader(data)
        assert reader.get_long() == -9007199254740992

    def test_get_ulong(self):
        """Test reading ulong / 测试读取无符号长整型"""
        data = struct.pack('<Q', 18000000000000000000)
        reader = NetDataReader(data)
        assert reader.get_ulong() == 18000000000000000000

    def test_get_float(self):
        """Test reading float / 测试读取浮点数"""
        data = struct.pack('<f', 3.14159)
        reader = NetDataReader(data)
        assert abs(reader.get_float() - 3.14159) < 0.00001

    def test_get_double(self):
        """Test reading double / 测试读取双精度"""
        data = struct.pack('<d', 3.141592653589793)
        reader = NetDataReader(data)
        assert abs(reader.get_double() - 3.141592653589793) < 1e-15

    def test_get_char(self):
        """Test reading char / 测试读取字符"""
        data = struct.pack('<H', ord('A'))
        reader = NetDataReader(data)
        assert reader.get_char() == 'A'


class TestDataReaderStrings:
    """Test DataReader string reading / 测试 DataReader 字符串读取"""

    def test_get_empty_string(self):
        """Test reading empty string / 测试读取空字符串"""
        data = struct.pack('<H', 0)
        reader = NetDataReader(data)
        assert reader.get_string() == ""

    def test_get_simple_string(self):
        """Test reading simple string / 测试读取简单字符串"""
        writer = NetDataWriter()
        writer.put_string("Hello")
        reader = NetDataReader(writer.to_bytes())
        assert reader.get_string() == "Hello"

    def test_get_string_utf8(self):
        """Test reading UTF-8 string / 测试读取 UTF-8 字符串"""
        writer = NetDataWriter()
        writer.put_string("你好世界")
        reader = NetDataReader(writer.to_bytes())
        assert reader.get_string() == "你好世界"

    def test_get_string_with_max_length(self):
        """Test reading string with max length / 测试读取带最大长度限制的字符串"""
        writer = NetDataWriter()
        writer.put_string("a" * 100)
        reader = NetDataReader(writer.to_bytes())
        result = reader.get_string(max_length=10)
        # Should return empty string if exceeds max_length
        assert result == ""

    def test_get_large_string(self):
        """Test reading large string / 测试读取大字符串"""
        writer = NetDataWriter()
        large_string = "x" * 100000
        writer.put_large_string(large_string)
        reader = NetDataReader(writer.to_bytes())
        assert reader.get_large_string() == large_string


class TestDataReaderBytes:
    """Test DataReader bytes reading / 测试 DataReader 字节读取"""

    def test_get_bytes(self):
        """Test reading bytes / 测试读取字节"""
        data = b'Hello World'
        reader = NetDataReader(data)
        result = reader.get_bytes(len(data))
        assert result == data

    def test_get_bytes_with_length(self):
        """Test reading bytes with length prefix / 测试读取带长度前缀的字节"""
        writer = NetDataWriter()
        original = b'Test Data'
        writer.put_bytes_with_length(original)
        reader = NetDataReader(writer.to_bytes())
        result = reader.get_bytes_with_length()
        assert result == original

    def test_get_remaining_bytes(self):
        """Test reading remaining bytes / 测试读取剩余字节"""
        data = b'HelloWorld'
        reader = NetDataReader(data)
        reader.skip_bytes(5)
        result = reader.get_remaining_bytes()
        assert result == b'World'


class TestDataReaderArrays:
    """Test DataReader array reading / 测试 DataReader 数组读取"""

    def test_get_empty_array(self):
        """Test reading empty array / 测试读取空数组"""
        data = struct.pack('<H', 0)
        reader = NetDataReader(data)
        result = reader.get_array(element_size=4)
        assert result == []

    def test_get_int_array(self):
        """Test reading int array / 测试读取整型数组"""
        writer = NetDataWriter()
        arr = [1, 2, 3, 4, 5]
        writer.put_array(arr, element_size=4)
        reader = NetDataReader(writer.to_bytes())
        result = reader.get_array(element_size=4)
        assert result == arr

    def test_get_string_array(self):
        """Test reading string array / 测试读取字符串数组"""
        writer = NetDataWriter()
        arr = ["Hello", "World", "Test"]
        writer.put_string_array(arr)
        reader = NetDataReader(writer.to_bytes())
        result = reader.get_string_array()
        assert result == arr


class TestDataReaderSpecialTypes:
    """Test DataReader special types / 测试 DataReader 特殊类型"""

    def test_get_uuid(self):
        """Test reading UUID / 测试读取 UUID"""
        test_uuid = uuid.uuid4()
        writer = NetDataWriter()
        writer.put_uuid(test_uuid)
        reader = NetDataReader(writer.to_bytes())
        result = reader.get_uuid()
        assert result == test_uuid

    def test_get_ip_end_point_ipv4(self):
        """Test reading IPv4 endpoint / 测试读取 IPv4 端点"""
        writer = NetDataWriter()
        writer.put_ip_end_point("192.168.1.1", 8080, 'IPv4')
        reader = NetDataReader(writer.to_bytes())
        address, port, family = reader.get_ip_end_point()
        assert address == "192.168.1.1"
        assert port == 8080
        assert family == 'IPv4'


class TestDataReaderPosition:
    """Test DataReader position management / 测试 DataReader 位置管理"""

    def test_position_property(self):
        """Test position property / 测试 position 属性"""
        data = b'HelloWorld'
        reader = NetDataReader(data)
        assert reader.position == 0
        reader.get_bytes(5)
        assert reader.position == 5

    def test_available_bytes(self):
        """Test available_bytes property / 测试 available_bytes 属性"""
        data = b'HelloWorld'
        reader = NetDataReader(data)
        assert reader.available_bytes == 10
        reader.get_bytes(5)
        assert reader.available_bytes == 5

    def test_end_of_data(self):
        """Test end_of_data property / 测试 end_of_data 属性"""
        data = b'Hello'
        reader = NetDataReader(data)
        assert not reader.end_of_data
        reader.get_bytes(5)
        assert reader.end_of_data

    def test_skip_bytes(self):
        """Test skip_bytes / 测试 skip_bytes"""
        data = b'HelloWorld'
        reader = NetDataReader(data)
        reader.skip_bytes(5)
        assert reader.position == 5
        assert reader.get_bytes(5) == b'World'

    def test_set_position(self):
        """Test set_position / 测试 set_position"""
        data = b'HelloWorld'
        reader = NetDataReader(data)
        reader.set_position(5)
        assert reader.position == 5
        assert reader.get_bytes(5) == b'World'


class TestDataReaderPeek:
    """Test DataReader peek methods / 测试 DataReader peek 方法"""

    def test_peek_byte(self):
        """Test peek_byte / 测试 peek_byte"""
        data = struct.pack('<B', 42)
        reader = NetDataReader(data)
        assert reader.peek_byte() == 42
        assert reader.position == 0  # Position shouldn't change

    def test_peek_bool(self):
        """Test peek_bool / 测试 peek_bool"""
        data = struct.pack('<B', 1)
        reader = NetDataReader(data)
        assert reader.peek_bool() is True
        assert reader.position == 0

    def test_peek_ushort(self):
        """Test peek_ushort / 测试 peek_ushort"""
        data = struct.pack('<H', 12345)
        reader = NetDataReader(data)
        assert reader.peek_ushort() == 12345
        assert reader.position == 0

    def test_peek_string(self):
        """Test peek_string / 测试 peek_string"""
        writer = NetDataWriter()
        writer.put_string("Hello")
        reader = NetDataReader(writer.to_bytes())
        result = reader.peek_string()
        assert result == "Hello"
        assert reader.position == 0


class TestDataReaderTryMethods:
    """Test DataReader try methods / 测试 DataReader try 方法"""

    def test_try_get_byte_success(self):
        """Test try_get_byte success / 测试 try_get_byte 成功"""
        data = struct.pack('<B', 42)
        reader = NetDataReader(data)
        success, value = reader.try_get_byte()
        assert success is True
        assert value == 42

    def test_try_get_byte_failure(self):
        """Test try_get_byte failure / 测试 try_get_byte 失败"""
        reader = NetDataReader(b'')
        success, value = reader.try_get_byte(default=99)
        assert success is False
        assert value == 99

    def test_try_get_int_success(self):
        """Test try_get_int success / 测试 try_get_int 成功"""
        data = struct.pack('<i', 12345)
        reader = NetDataReader(data)
        success, value = reader.try_get_int()
        assert success is True
        assert value == 12345

    def test_try_get_string_success(self):
        """Test try_get_string success / 测试 try_get_string 成功"""
        writer = NetDataWriter()
        writer.put_string("Hello")
        reader = NetDataReader(writer.to_bytes())
        success, value = reader.try_get_string()
        assert success is True
        assert value == "Hello"


class TestRoundTrip:
    """Test write-read round trip / 测试写入读取往返"""

    def test_round_trip_all_types(self):
        """Test round trip for all types / 测试所有类型的往返"""
        writer = NetDataWriter()

        # Write all types
        writer.put_byte(42)
        writer.put_short(-1000)
        writer.put_int(123456789)
        writer.put_long(-9007199254740992)
        writer.put_float(3.14159)
        writer.put_double(2.718281828459045)
        writer.put_string("Hello, World!")
        writer.put_bool(True)
        writer.put_bytes(b'Raw Data')

        # Read back
        reader = NetDataReader(writer.to_bytes())
        assert reader.get_byte() == 42
        assert reader.get_short() == -1000
        assert reader.get_int() == 123456789
        assert reader.get_long() == -9007199254740992
        assert abs(reader.get_float() - 3.14159) < 0.00001
        assert abs(reader.get_double() - 2.718281828459045) < 1e-15
        assert reader.get_string() == "Hello, World!"
        assert reader.get_bool() is True
        assert reader.get_bytes(8) == b'Raw Data'

    def test_round_trip_complex_data(self):
        """Test round trip with complex data / 测试复杂数据的往返"""
        writer = NetDataWriter()

        test_uuid = uuid.uuid4()
        writer.put_uuid(test_uuid)

        test_array = [1, 2, 3, 4, 5]
        writer.put_array(test_array, element_size=4)

        test_strings = ["Hello", "World", "Test"]
        writer.put_string_array(test_strings)

        reader = NetDataReader(writer.to_bytes())
        assert reader.get_uuid() == test_uuid
        assert reader.get_array(element_size=4) == test_array
        assert reader.get_string_array() == test_strings


class TestEndianness:
    """Test little-endian byte order / 测试小端字节序"""

    def test_int_little_endian(self):
        """Test int is little-endian / 测试整型为小端"""
        writer = NetDataWriter()
        writer.put_int(0x12345678)
        # Little-endian: 78 56 34 12
        assert writer.data[0] == 0x78
        assert writer.data[1] == 0x56
        assert writer.data[2] == 0x34
        assert writer.data[3] == 0x12

    def test_long_little_endian(self):
        """Test long is little-endian / 测试长整型为小端"""
        writer = NetDataWriter()
        writer.put_long(0x123456789ABCDEF0)
        # Little-endian: F0 DE BC 9A 78 56 34 12
        expected = [0xF0, 0xDE, 0xBC, 0x9A, 0x78, 0x56, 0x34, 0x12]
        for i, expected_byte in enumerate(expected):
            assert writer.data[i] == expected_byte


class TestBoundaryConditions:
    """Test boundary conditions / 测试边界条件"""

    def test_empty_reader(self):
        """Test reading from empty reader / 测试从空 reader 读取"""
        reader = NetDataReader(b'')
        assert reader.is_null
        assert reader.end_of_data
        assert reader.available_bytes == 0

    def test_read_beyond_data(self):
        """Test reading beyond available data / 测试读取超出可用数据"""
        reader = NetDataReader(b'Hi')  # Only 2 bytes
        with pytest.raises(EOFError):
            reader.get_int()  # Need 4 bytes, only have 2

    def test_write_auto_resize(self):
        """Test auto resize / 测试自动调整大小"""
        writer = NetDataWriter(initial_size=10)
        # Write more than initial capacity
        writer.put_bytes(b'x' * 100)
        assert writer.capacity >= 100

    def test_max_values(self):
        """Test maximum values / 测试最大值"""
        writer = NetDataWriter()
        writer.put_byte(255)
        writer.put_ushort(65535)
        writer.put_uint(0xFFFFFFFF)
        writer.put_ulong(0xFFFFFFFFFFFFFFFF)

        reader = NetDataReader(writer.to_bytes())
        assert reader.get_byte() == 255
        assert reader.get_ushort() == 65535
        assert reader.get_uint() == 0xFFFFFFFF
        assert reader.get_ulong() == 0xFFFFFFFFFFFFFFFF


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
