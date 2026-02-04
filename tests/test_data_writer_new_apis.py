"""
Tests for NetDataWriter new APIs.

Tests all newly added methods including factory methods, resize methods,
and array writing methods.
"""

import pytest
from litenetlib.utils.data_writer import NetDataWriter
from litenetlib.utils.data_reader import NetDataReader


class TestFactoryMethods:
    """Test static factory methods."""

    def test_from_bytes_with_copy(self):
        """Test creating writer from bytes with copy."""
        data = b"HelloWorld"
        writer = NetDataWriter.from_bytes(data, copy=True)
        assert writer.to_bytes() == data
        assert writer.length == len(data)

    def test_from_bytes_without_copy(self):
        """Test creating writer from bytes without copy."""
        data = b"TestData"
        writer = NetDataWriter.from_bytes(data, copy=False)
        assert writer.to_bytes() == data
        assert writer.length == len(data)

    def test_from_bytes_with_offset(self):
        """Test creating writer from bytes with offset."""
        data = b"0123456789ABCDEFGHIJ"
        writer = NetDataWriter.from_bytes_with_offset(data, 10, 10)
        result = writer.to_bytes()
        assert result == b"ABCDEFGHIJ"
        assert writer.length == 10

    def test_from_bytes_with_offset_partial(self):
        """Test creating writer from bytes with partial offset."""
        data = b"0123456789ABCDEFGHIJKLMNOPQRSTUV"
        writer = NetDataWriter.from_bytes_with_offset(data, 10, 5)
        result = writer.to_bytes()
        assert result == b"ABCDE"
        assert writer.length == 5

    def test_from_string(self):
        """Test creating writer from string."""
        writer = NetDataWriter.from_string("TestString")
        result = writer.to_bytes()
        # Should write string with length prefix
        reader = NetDataReader(result)
        assert reader.get_string() == "TestString"


class TestResizeMethods:
    """Test buffer resize methods."""

    def test_resize_if_need_no_resize(self):
        """Test resize_if_need when resize not needed."""
        writer = NetDataWriter(initial_size=100)
        writer.put_int(42)
        # Should not raise
        writer.resize_if_need(50)
        assert writer.length == 4

    def test_resize_if_need_with_resize(self):
        """Test resize_if_need when resize needed."""
        writer = NetDataWriter(initial_size=4, auto_resize=True)
        writer.resize_if_need(100)
        # Buffer should be resized
        assert writer.capacity >= 100

    def test_ensure_fit_small_addition(self):
        """Test ensure_fit with small addition."""
        writer = NetDataWriter(initial_size=10)
        writer.ensure_fit(5)
        assert writer.capacity >= 5

    def test_ensure_fit_large_addition(self):
        """Test ensure_fit with large addition."""
        writer = NetDataWriter(initial_size=10)
        writer.ensure_fit(1000)
        assert writer.capacity >= 1000

    def test_ensure_fit_no_auto_resize(self):
        """Test ensure_fit without auto resize."""
        writer = NetDataWriter(initial_size=10, auto_resize=False)
        writer.ensure_fit(100)
        # Should not resize
        assert writer.capacity == 10


class TestArrayMethods:
    """Test array writing methods."""

    def test_put_bool_array(self):
        """Test writing bool array."""
        writer = NetDataWriter()
        writer.put_bool_array([True, False, True, True, False])
        reader = NetDataReader(writer.to_bytes())
        assert reader.get_bool_array() == [True, False, True, True, False]

    def test_put_bool_array_empty(self):
        """Test writing empty bool array."""
        writer = NetDataWriter()
        writer.put_bool_array([])
        reader = NetDataReader(writer.to_bytes())
        assert reader.get_bool_array() == []

    def test_put_short_array(self):
        """Test writing short array."""
        writer = NetDataWriter()
        writer.put_short_array([100, -200, 300, -400])
        reader = NetDataReader(writer.to_bytes())
        assert reader.get_short_array() == [100, -200, 300, -400]

    def test_put_ushort_array(self):
        """Test writing ushort array."""
        writer = NetDataWriter()
        writer.put_ushort_array([1000, 20000, 40000, 65535])
        reader = NetDataReader(writer.to_bytes())
        assert reader.get_ushort_array() == [1000, 20000, 40000, 65535]

    def test_put_int_array(self):
        """Test writing int array."""
        writer = NetDataWriter()
        writer.put_int_array([100000, -200000, 300000, -400000])
        reader = NetDataReader(writer.to_bytes())
        assert reader.get_int_array() == [100000, -200000, 300000, -400000]

    def test_put_uint_array(self):
        """Test writing uint array."""
        writer = NetDataWriter()
        writer.put_uint_array([1000000, 2000000, 3000000, 4000000])
        reader = NetDataReader(writer.to_bytes())
        assert reader.get_uint_array() == [1000000, 2000000, 3000000, 4000000]

    def test_put_long_array(self):
        """Test writing long array."""
        writer = NetDataWriter()
        writer.put_long_array([123456789012, -987654321098])
        reader = NetDataReader(writer.to_bytes())
        assert reader.get_long_array() == [123456789012, -987654321098]

    def test_put_ulong_array(self):
        """Test writing ulong array."""
        writer = NetDataWriter()
        writer.put_ulong_array([123456789012, 18446744073709551615])
        reader = NetDataReader(writer.to_bytes())
        assert reader.get_ulong_array() == [123456789012, 18446744073709551615]

    def test_put_float_array(self):
        """Test writing float array."""
        writer = NetDataWriter()
        writer.put_float_array([1.1, 2.2, 3.3, 4.4])
        reader = NetDataReader(writer.to_bytes())
        result = reader.get_float_array()
        assert len(result) == 4
        assert abs(result[0] - 1.1) < 0.01
        assert abs(result[1] - 2.2) < 0.01
        assert abs(result[2] - 3.3) < 0.01
        assert abs(result[3] - 4.4) < 0.01

    def test_put_double_array(self):
        """Test writing double array."""
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

    def test_put_sbytes_with_length(self):
        """Test writing sbytes with length prefix."""
        writer = NetDataWriter()
        writer.put_sbytes_with_length(b"TestData")
        reader = NetDataReader(writer.to_bytes())
        result = reader.get_sbytes_with_length()
        assert result == b"TestData"

    def test_put_sbytes_with_length_empty(self):
        """Test writing empty sbytes with length."""
        writer = NetDataWriter()
        writer.put_sbytes_with_length(b"")
        reader = NetDataReader(writer.to_bytes())
        result = reader.get_sbytes_with_length()
        assert result == b""

    def test_capacity_property(self):
        """Test capacity property."""
        writer = NetDataWriter(initial_size=100)
        assert writer.capacity >= 100

    def test_length_property(self):
        """Test length property."""
        writer = NetDataWriter()
        assert writer.length == 0
        writer.put_int(42)
        assert writer.length == 4
        writer.put_short(100)
        assert writer.length == 6

    def test_set_position(self):
        """Test set_position returns previous position."""
        writer = NetDataWriter()
        writer.put_int(42)
        writer.put_int(43)
        assert writer.length == 8

        prev = writer.set_position(4)
        assert prev == 8
        assert writer.length == 4

        writer.put_int(44)
        assert writer.length == 8

    def test_data_property(self):
        """Test data property returns bytearray."""
        writer = NetDataWriter()
        writer.put_int(42)
        data = writer.data
        assert isinstance(data, bytearray)
        assert len(data) >= 4


class TestEdgeCases:
    """Test edge cases and special scenarios."""

    def test_put_none_array(self):
        """Test writing None array."""
        writer = NetDataWriter()
        writer.put_int_array(None)
        reader = NetDataReader(writer.to_bytes())
        assert reader.get_int_array() == []

    def test_large_array(self):
        """Test writing large array."""
        writer = NetDataWriter()
        large_array = list(range(1000))
        writer.put_int_array(large_array)
        reader = NetDataReader(writer.to_bytes())
        result = reader.get_int_array()
        assert result == large_array

    def test_mixed_array_types(self):
        """Test writing multiple different array types."""
        writer = NetDataWriter()
        writer.put_bool_array([True, False])
        writer.put_short_array([1, 2, 3])
        writer.put_int_array([100, 200])
        writer.put_long_array([1000, 2000])

        reader = NetDataReader(writer.to_bytes())
        assert reader.get_bool_array() == [True, False]
        assert reader.get_short_array() == [1, 2, 3]
        assert reader.get_int_array() == [100, 200]
        assert reader.get_long_array() == [1000, 2000]


class TestRoundTrip:
    """Test round-trip write and read."""

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

        writer.put_bool_array(bool_arr)
        writer.put_short_array(short_arr)
        writer.put_ushort_array(ushort_arr)
        writer.put_int_array(int_arr)
        writer.put_uint_array(uint_arr)
        writer.put_long_array(long_arr)
        writer.put_ulong_array(ulong_arr)
        writer.put_float_array(float_arr)
        writer.put_double_array(double_arr)

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
            assert abs(a - b) < 0.01

        double_result = reader.get_double_array()
        assert len(double_result) == len(double_arr)
        for i, (a, b) in enumerate(zip(double_result, double_arr)):
            assert abs(a - b) < 0.0000001

    def test_factory_method_round_trip(self):
        """Test from_bytes factory method round-trip."""
        original = NetDataWriter()
        original.put_int(42)
        original.put_string("Test")
        original.put_bool_array([True, False, True])

        data = original.to_bytes()

        # Create new writer from bytes
        new_writer = NetDataWriter.from_bytes(data)

        # Read and verify
        reader = NetDataReader(new_writer.to_bytes())
        assert reader.get_int() == 42
        assert reader.get_string() == "Test"
        assert reader.get_bool_array() == [True, False, True]
