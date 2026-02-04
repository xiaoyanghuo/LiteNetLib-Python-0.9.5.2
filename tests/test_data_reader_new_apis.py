"""
Tests for NetDataReader new APIs.

Tests all newly added methods including peek, try_get, arrays, and special methods.
"""

import pytest
import struct
from litenetlib.utils.data_reader import NetDataReader
from litenetlib.utils.data_writer import NetDataWriter


class TestPeekMethods:
    """Test peek methods (read without advancing position)."""

    def test_peek_sbyte_positive(self):
        """Test peeking positive signed byte."""
        writer = NetDataWriter()
        writer.put_sbyte(100)
        reader = NetDataReader(writer.to_bytes())
        assert reader.peek_sbyte() == 100
        assert reader.position == 0  # Position not advanced

    def test_peek_sbyte_negative(self):
        """Test peeking negative signed byte."""
        writer = NetDataWriter()
        writer.put_sbyte(-50)
        reader = NetDataReader(writer.to_bytes())
        assert reader.peek_sbyte() == -50
        assert reader.position == 0

    def test_peek_char(self):
        """Test peeking char."""
        writer = NetDataWriter()
        writer.put_char('A')
        reader = NetDataReader(writer.to_bytes())
        assert reader.peek_char() == 'A'
        assert reader.position == 0

    def test_peek_short(self):
        """Test peeking short."""
        writer = NetDataWriter()
        writer.put_short(-1000)
        reader = NetDataReader(writer.to_bytes())
        assert reader.peek_short() == -1000
        assert reader.position == 0

    def test_peek_long(self):
        """Test peeking long."""
        writer = NetDataWriter()
        writer.put_long(12345678901234)
        reader = NetDataReader(writer.to_bytes())
        assert reader.peek_long() == 12345678901234
        assert reader.position == 0

    def test_peek_ulong(self):
        """Test peeking unsigned long."""
        writer = NetDataWriter()
        writer.put_ulong(18446744073709551615)
        reader = NetDataReader(writer.to_bytes())
        assert reader.peek_ulong() == 18446744073709551615
        assert reader.position == 0

    def test_peek_int(self):
        """Test peeking int."""
        writer = NetDataWriter()
        writer.put_int(42)
        reader = NetDataReader(writer.to_bytes())
        assert reader.peek_int() == 42
        assert reader.position == 0

    def test_peek_uint(self):
        """Test peeking unsigned int."""
        writer = NetDataWriter()
        writer.put_uint(4000000000)
        reader = NetDataReader(writer.to_bytes())
        assert reader.peek_uint() == 4000000000
        assert reader.position == 0

    def test_peek_float(self):
        """Test peeking float."""
        writer = NetDataWriter()
        writer.put_float(3.14159)
        reader = NetDataReader(writer.to_bytes())
        assert abs(reader.peek_float() - 3.14159) < 0.00001
        assert reader.position == 0

    def test_peek_double(self):
        """Test peeking double."""
        writer = NetDataWriter()
        writer.put_double(2.718281828459)
        reader = NetDataReader(writer.to_bytes())
        assert abs(reader.peek_double() - 2.718281828459) < 0.0000001
        assert reader.position == 0

    def test_peek_then_read(self):
        """Test peek then actual read gives same value."""
        writer = NetDataWriter()
        writer.put_int(12345)
        reader = NetDataReader(writer.to_bytes())
        assert reader.peek_int() == 12345
        assert reader.get_int() == 12345


class TestTryGetMethods:
    """Test try_get methods (safe read with default values)."""

    def test_try_get_byte_success(self):
        """Test successful try_get_byte."""
        reader = NetDataReader(struct.pack('<B', 42))
        success, value = reader.try_get_byte()
        assert success is True
        assert value == 42

    def test_try_get_byte_failure(self):
        """Test failed try_get_byte."""
        reader = NetDataReader(b'')
        success, value = reader.try_get_byte(default=99)
        assert success is False
        assert value == 99

    def test_try_get_sbyte_success(self):
        """Test successful try_get_sbyte."""
        reader = NetDataReader(struct.pack('<b', -50))
        success, value = reader.try_get_sbyte()
        assert success is True
        assert value == -50

    def test_try_get_short_success(self):
        """Test successful try_get_short."""
        reader = NetDataReader(struct.pack('<h', -1000))
        success, value = reader.try_get_short()
        assert success is True
        assert value == -1000

    def test_try_get_ushort_success(self):
        """Test successful try_get_ushort."""
        reader = NetDataReader(struct.pack('<H', 50000))
        success, value = reader.try_get_ushort()
        assert success is True
        assert value == 50000

    def test_try_get_int_success(self):
        """Test successful try_get_int."""
        reader = NetDataReader(struct.pack('<i', 123456))
        success, value = reader.try_get_int()
        assert success is True
        assert value == 123456

    def test_try_get_uint_success(self):
        """Test successful try_get_uint."""
        reader = NetDataReader(struct.pack('<I', 3000000000))
        success, value = reader.try_get_uint()
        assert success is True
        assert value == 3000000000

    def test_try_get_long_success(self):
        """Test successful try_get_long."""
        reader = NetDataReader(struct.pack('<q', 12345678901234))
        success, value = reader.try_get_long()
        assert success is True
        assert value == 12345678901234

    def test_try_get_ulong_success(self):
        """Test successful try_get_ulong."""
        reader = NetDataReader(struct.pack('<Q', 18446744073709551615))
        success, value = reader.try_get_ulong()
        assert success is True
        assert value == 18446744073709551615

    def test_try_get_float_success(self):
        """Test successful try_get_float."""
        reader = NetDataReader(struct.pack('<f', 3.14))
        success, value = reader.try_get_float()
        assert success is True
        assert abs(value - 3.14) < 0.01

    def test_try_get_double_success(self):
        """Test successful try_get_double."""
        reader = NetDataReader(struct.pack('<d', 2.718281828459))
        success, value = reader.try_get_double()
        assert success is True
        assert abs(value - 2.718281828459) < 0.0000001

    def test_try_get_string_success(self):
        """Test successful try_get_string."""
        writer = NetDataWriter()
        writer.put_string("Hello")
        reader = NetDataReader(writer.to_bytes())
        success, value = reader.try_get_string()
        assert success is True
        assert value == "Hello"

    def test_try_get_bytes_with_length_success(self):
        """Test successful try_get_bytes_with_length."""
        writer = NetDataWriter()
        writer.put_bytes_with_length(b"TestData")
        reader = NetDataReader(writer.to_bytes())
        success, value = reader.try_get_bytes_with_length()
        assert success is True
        assert value == b"TestData"


class TestArrayMethods:
    """Test array reading methods."""

    def test_get_bool_array(self):
        """Test reading bool array."""
        writer = NetDataWriter()
        writer.put_bool_array([True, False, True, True, False])
        reader = NetDataReader(writer.to_bytes())
        result = reader.get_bool_array()
        assert result == [True, False, True, True, False]

    def test_get_bool_array_empty(self):
        """Test reading empty bool array."""
        writer = NetDataWriter()
        writer.put_bool_array([])
        reader = NetDataReader(writer.to_bytes())
        result = reader.get_bool_array()
        assert result == []

    def test_get_short_array(self):
        """Test reading short array."""
        writer = NetDataWriter()
        writer.put_short_array([100, -200, 300, -400])
        reader = NetDataReader(writer.to_bytes())
        result = reader.get_short_array()
        assert result == [100, -200, 300, -400]

    def test_get_ushort_array(self):
        """Test reading ushort array."""
        writer = NetDataWriter()
        writer.put_ushort_array([1000, 20000, 40000, 65535])
        reader = NetDataReader(writer.to_bytes())
        result = reader.get_ushort_array()
        assert result == [1000, 20000, 40000, 65535]

    def test_get_int_array(self):
        """Test reading int array."""
        writer = NetDataWriter()
        writer.put_int_array([100000, -200000, 300000, -400000])
        reader = NetDataReader(writer.to_bytes())
        result = reader.get_int_array()
        assert result == [100000, -200000, 300000, -400000]

    def test_get_uint_array(self):
        """Test reading uint array."""
        writer = NetDataWriter()
        writer.put_uint_array([1000000, 2000000, 3000000, 4000000])
        reader = NetDataReader(writer.to_bytes())
        result = reader.get_uint_array()
        assert result == [1000000, 2000000, 3000000, 4000000]

    def test_get_long_array(self):
        """Test reading long array."""
        writer = NetDataWriter()
        writer.put_long_array([123456789012, -987654321098])
        reader = NetDataReader(writer.to_bytes())
        result = reader.get_long_array()
        assert result == [123456789012, -987654321098]

    def test_get_ulong_array(self):
        """Test reading ulong array."""
        writer = NetDataWriter()
        writer.put_ulong_array([123456789012, 18446744073709551615])
        reader = NetDataReader(writer.to_bytes())
        result = reader.get_ulong_array()
        assert result == [123456789012, 18446744073709551615]

    def test_get_float_array(self):
        """Test reading float array."""
        writer = NetDataWriter()
        writer.put_float_array([1.1, 2.2, 3.3, 4.4])
        reader = NetDataReader(writer.to_bytes())
        result = reader.get_float_array()
        assert len(result) == 4
        assert abs(result[0] - 1.1) < 0.01
        assert abs(result[1] - 2.2) < 0.01
        assert abs(result[2] - 3.3) < 0.01
        assert abs(result[3] - 4.4) < 0.01

    def test_get_double_array(self):
        """Test reading double array."""
        writer = NetDataWriter()
        writer.put_double_array([1.1111111, 2.2222222, 3.3333333])
        reader = NetDataReader(writer.to_bytes())
        result = reader.get_double_array()
        assert len(result) == 3
        assert abs(result[0] - 1.1111111) < 0.0000001
        assert abs(result[1] - 2.2222222) < 0.0000001
        assert abs(result[2] - 3.3333333) < 0.0000001


class TestSpecialMethods:
    """Test special utility methods."""

    def test_get_sbytes_with_length(self):
        """Test reading sbytes with length prefix."""
        writer = NetDataWriter()
        writer.put_sbytes_with_length(b"TestData")
        reader = NetDataReader(writer.to_bytes())
        result = reader.get_sbytes_with_length()
        assert result == b"TestData"

    def test_get_remaining_bytes_segment(self):
        """Test reading remaining bytes segment."""
        writer = NetDataWriter()
        writer.put_int(42)
        writer.put_int(43)
        reader = NetDataReader(writer.to_bytes())
        reader.get_int()  # Read first int
        remaining = reader.get_remaining_bytes_segment()
        assert len(remaining) == 4  # One int remaining
        assert reader.end_of_data

    def test_raw_data_property(self):
        """Test raw_data property."""
        data = struct.pack('<i', 12345)
        reader = NetDataReader(data)
        assert reader.raw_data.tobytes() == data

    def test_raw_data_size_property(self):
        """Test raw_data_size property."""
        data = struct.pack('<ii', 1, 2)
        reader = NetDataReader(data)
        assert reader.raw_data_size == 8

    def test_get_bytes_count_only(self):
        """Test get_bytes with count parameter only."""
        data = b"HelloWorld"
        reader = NetDataReader(data)
        result = reader.get_bytes(5)
        assert result == b"Hello"
        assert reader.position == 5

    def test_get_bytes_with_destination(self):
        """Test get_bytes into destination array."""
        source_data = b"ABCDEFGHIJ"
        reader = NetDataReader(source_data)
        dest = bytearray(10)  # Create destination with space
        reader.get_bytes(5, dest, 0)  # count, destination, start
        assert dest[:5] == b"ABCDE"
        assert reader.position == 5


class TestEdgeCases:
    """Test edge cases and error conditions."""

    def test_peek_empty_reader(self):
        """Test peek on empty reader raises error."""
        reader = NetDataReader(b'')
        with pytest.raises(EOFError):
            reader.peek_byte()

    def test_try_get_on_empty_reader(self):
        """Test try_get on empty reader returns default."""
        reader = NetDataReader(b'')
        success, value = reader.try_get_int(default=999)
        assert success is False
        assert value == 999

    def test_get_array_empty(self):
        """Test reading empty array."""
        writer = NetDataWriter()
        writer.put_ushort(0)  # Empty array
        reader = NetDataReader(writer.to_bytes())
        result = reader.get_array(4)
        assert result == []

    def test_peek_multiple_times(self):
        """Test peeking multiple times without advancing."""
        writer = NetDataWriter()
        writer.put_int(42)
        reader = NetDataReader(writer.to_bytes())
        assert reader.peek_int() == 42
        assert reader.peek_int() == 42
        assert reader.peek_int() == 42
        assert reader.position == 0


class TestRoundTripWithWriter:
    """Test round-trip with NetDataWriter."""

    def test_all_array_types_round_trip(self):
        """Test all array types round-trip."""
        writer = NetDataWriter()

        bool_arr = [True, False, True]
        short_arr = [100, -200, 300]
        ushort_arr = [1000, 20000, 40000]
        int_arr = [100000, -200000]
        uint_arr = [1000000, 2000000]
        long_arr = [123456789012, -987654321098]
        ulong_arr = [123456789012, 18446744073709551615]
        float_arr = [1.1, 2.2, 3.3]
        double_arr = [1.1111111, 2.2222222]
        str_arr = ["Hello", "World", "Test"]

        writer.put_bool_array(bool_arr)
        writer.put_short_array(short_arr)
        writer.put_ushort_array(ushort_arr)
        writer.put_int_array(int_arr)
        writer.put_uint_array(uint_arr)
        writer.put_long_array(long_arr)
        writer.put_ulong_array(ulong_arr)
        writer.put_float_array(float_arr)
        writer.put_double_array(double_arr)
        writer.put_string_array(str_arr)

        reader = NetDataReader(writer.to_bytes())

        assert reader.get_bool_array() == bool_arr
        assert reader.get_short_array() == short_arr
        assert reader.get_ushort_array() == ushort_arr
        assert reader.get_int_array() == int_arr
        assert reader.get_uint_array() == uint_arr
        assert reader.get_long_array() == long_arr
        assert reader.get_ulong_array() == ulong_arr

        float_result = reader.get_float_array()
        assert len(float_result) == len(float_arr)
        for i, (a, b) in enumerate(zip(float_result, float_arr)):
            assert abs(a - b) < 0.01  # Float precision tolerance

        double_result = reader.get_double_array()
        assert len(double_result) == len(double_arr)
        for i, (a, b) in enumerate(zip(double_result, double_arr)):
            assert abs(a - b) < 0.0000001  # Double precision tolerance

        assert reader.get_string_array() == str_arr
